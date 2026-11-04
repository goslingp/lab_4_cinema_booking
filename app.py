from flask import Flask, request, jsonify, render_template

app = Flask(__name__)

# -----------------------------
# Pricing Rules
# -----------------------------
PRICES = {
    "child": 8,
    "teen": 10,
    "adult": 15,
    "senior": 12
}



# Your existing pricing logic and /calculate route goes here…

@app.route("/")
def booking_form():
    return render_template("booking.html")


# -----------------------------
# Helper Functions
# -----------------------------

def classify_age(age):
    """Return the age category or None if invalid."""
    if not isinstance(age, int):
        return None
    if age < 0 or age > 120:
        return None
    if age <= 12:
        return "child"
    elif age <= 17:
        return "teen"
    elif age <= 64:
        return "adult"
    else:
        return "senior"


def apply_discounts(category, base_price, is_student, total_tickets):
    """
    Apply discount rules:
    - Student discount: 10% off teen/adult
    - Group discount: 5% off total if >= 6 tickets
    - Senior discount already included in base price
    - No stacking: student discount OR group discount, not both
    """
    price = base_price

    # Student discount applies only to teen/adult
    student_applicable = is_student and category in ["teen", "adult"]

    # Group discount applies to entire order
    group_applicable = total_tickets >= 6

    # No stacking: student discount takes priority
    if student_applicable:
        price *= 0.90
    elif group_applicable:
        price *= 0.95

    return round(price, 2)


# -----------------------------
# Routes
# -----------------------------

@app.route("/calculate", methods=["POST"])
def calculate():
    data = request.get_json()

    # Validate ticket quantity
    tickets = data.get("tickets")
    if not isinstance(tickets, int) or tickets < 1 or tickets > 10:
        return jsonify({"error": "Tickets must be an integer between 1 and 10"}), 400

    # Validate ages list
    ages = data.get("ages")
    if not isinstance(ages, list) or len(ages) != tickets:
        return jsonify({"error": "Ages list must match number of tickets"}), 400

    # Student flag
    is_students = data.get("students")   
    is_student = bool(data.get("student", False))

    breakdown = []
    total_cost = 0

    for age,is_student in zip(ages, is_students):
        category = classify_age(age)
        if category is None:
            return jsonify({"error": f"Invalid age value: {age}"}), 400

        base_price = PRICES[category]
        final_price = apply_discounts(category, base_price, is_student, tickets)

        breakdown.append({
            "age": age,
            "category": category,
            "base_price": base_price,
            "final_price": final_price
        })

        total_cost += final_price

    return jsonify({
        "tickets": tickets,
        "student_discount": is_student,
        "breakdown": breakdown,
        "total_cost": round(total_cost, 2)
    })


# -----------------------------
# Run the app
# -----------------------------
if __name__ == "__main__":
    app.run(debug=True)
