const salesCards = document.querySelectorAll('.sales__card')

salesCards.forEach(card => {
    card.addEventListener('click', function(event){
        event.stopPropagation();

        const expandedCard = document.querySelector('.sales__card.expanded');
        if (expandedCard && expandedCard !== this) {
            expandedCard.classList.remove('expanded');
        }

        this.classList.toggle('expanded');
    });
});

document.querySelectorAll('.sales__card--content').forEach(content => {
    content.addEventListener('click', function (event) {
        event.stopPropagation(); // Prevent clicks inside from closing the card
    });
});

document.getElementById("customerName").addEventListener("change", function() {
    let customerName = this.value;

    fetch(`/suggest_customer?name=${customerName}`)
    .then(response => response.json())
    .then(data => {
        document.getElementById("customerPhone").value = data.phone || "";
        document.getElementById("customerAddress").value = data.address || "";
    })
    .catch(error => console.error("Error fetching customer data:", error));
});

document.querySelectorAll(".sales__row--add").forEach(button => {
    button.addEventListener("click", function() {
        let table = this.closest("table").querySelector(".sales__row");

        let newRow = document.createElement("tr");

        // Create and append input fields for product data
        newRow.innerHTML = `
            <td><input type="text" name="productName[]" list="products" autocomplete="off"></td>
            <td><input type="number" name="quantity[]" autocomplete="off"></td>
            <td><input type="number" name="price[]" autocomplete="off"></td>
            <td><button type="button" class="sales__row--remove">Remove</button></td>
        `;

        // Append the new row to the table
        table.appendChild(newRow);

        // Attach event to remove the row
        newRow.querySelector(".sales__row--remove").addEventListener("click", function() {
            table.removeChild(newRow);
        });
    });
});