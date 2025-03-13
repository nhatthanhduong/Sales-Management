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

document.querySelectorAll(".procurement__row--add").forEach(button => {
    button.addEventListener("click", function() {
        let table = this.closest("table").querySelector(".procurement__row");

        let newRow = document.createElement("tr");

        // Create and append input fields for product data
        newRow.innerHTML = `
            <td><input type="text" name="productName[]" list="products" autocomplete="off"></td>
            <td><input type="text" name="productCategory[]" autocomplete="off"></td>
            <td><input type="text" name="productDescription[]" autocomplete="off"></td>
            <td><input type="text" name="unit[]" autocomplete="off"></td>
            <td><input type="text" name="purchasingPrice[]" autocomplete="off"></td>
            <td><input type="text" name="sellingPrice[]" autocomplete="off"></td>
            <td><button type="button" class="procurement__row--remove">Remove</button></td>
        `;

        // Append the new row to the table
        table.appendChild(newRow);

        // Attach event to remove the row
        newRow.querySelector(".procurement__row--remove").addEventListener("click", function() {
            table.removeChild(newRow);
        });
    });
});