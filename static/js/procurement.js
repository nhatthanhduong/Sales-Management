const salesCards = document.querySelectorAll('.sales__card')

function formatNumberWithCommas(number) {
    return Number(number).toLocaleString(); 
}

function formatAllNumbers() {
    const elements = document.querySelectorAll('td');
    
    elements.forEach(element => {
        if (element.textContent.trim() !== '') {
            const hasButton = element.querySelector('button');
            
            if (hasButton) {
                return;
            }
            element.textContent = element.textContent.replace(/\d+/g, (match) => formatNumberWithCommas(match));
        }
    });
}
window.onload = formatAllNumbers;

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
        event.stopPropagation();
    });
});

document.addEventListener('click', function(event) {
    const expandedCard = document.querySelector('.sales__card.expanded');
    if (expandedCard && !expandedCard.contains(event.target)) {
        expandedCard.classList.remove('expanded');
    }
});

document.querySelectorAll(".procurement__row--add").forEach(button => {
    button.addEventListener("click", function() {
        let table = this.closest("table").querySelector(".procurement__row");

        let newRow = document.createElement("tr");

        newRow.innerHTML = `
            <td><input type="text" name="productName[]" list="products" autocomplete="off"></td>
            <td><input type="text" name="productCategory[]" autocomplete="off"></td>
            <td><input type="text" name="productDescription[]" autocomplete="off"></td>
            <td><input type="text" name="unit[]" autocomplete="off"></td>
            <td><input type="text" name="purchasingPrice[]" autocomplete="off"></td>
            <td><input type="text" name="sellingPrice[]" autocomplete="off"></td>
            <td><button type="button" class="procurement__row--remove">Remove</button></td>
        `;

        table.appendChild(newRow);

        newRow.querySelector(".procurement__row--remove").addEventListener("click", function() {
            table.removeChild(newRow);
        });
    });
});