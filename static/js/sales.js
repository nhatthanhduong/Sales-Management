const salescards = document.querySelectorAll('.sales__card')

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
window.onload = function() {
    formatAllNumbers();
    
    const totalDebtElement = document.getElementById('total__debt');
    const rawTotalDebtElement = document.getElementById('raw_total_debt');

    if (totalDebtElement && rawTotalDebtElement) {
        const totalDebt = parseFloat(rawTotalDebtElement.textContent.replace(/,/g, ''));
        if (!isNaN(totalDebt)) {
            totalDebtElement.textContent = "Total Debt: " + formatNumberWithCommas(totalDebt);
        }
    }
};

salescards.forEach(card => {
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

function deleteProduct(salesOrderID, productID, orderType) {
    if (confirm("Are you sure you want to delete this product?")) {
        let form = document.createElement("form");
        form.method = "POST";
        if (orderType == 'finalizing'){
            form.action = "/sales/update_finalizing_order";
        }
        else if (orderType == 'delivering'){
            form.action = "/sales/update_delivering_order";
        }

        let salesOrderInput = document.createElement("input");
        salesOrderInput.type = "hidden";
        salesOrderInput.name = "salesOrderID";
        salesOrderInput.value = salesOrderID;
        form.appendChild(salesOrderInput);

        let productInput = document.createElement("input");
        productInput.type = "hidden";
        productInput.name = "productID";
        productInput.value = productID;
        form.appendChild(productInput);

        let actionInput = document.createElement("input");
        actionInput.type = "hidden";
        actionInput.name = "action";
        actionInput.value = "delete";
        form.appendChild(actionInput);

        document.body.appendChild(form);
        form.submit();
    }
}

document.querySelectorAll(".sales__row--add").forEach(button => {
    button.addEventListener("click", function() {
        let table = this.closest("table");
        let tbody = table.querySelector(".sales__row");
      
        let columnCount = table.querySelector("thead tr").children.length;

        let newRow = document.createElement("tr");

        if (columnCount === 3) {
            newRow.innerHTML = `
                <td><input type="text" name="productName[]" list="products" autocomplete="off"></td>
                <td><input type="number" name="quantity[]" autocomplete="off"></td>
                <td><button type="button" class="sales__row--remove">Remove</button></td>
            `;
        } else if (columnCount === 4) {
            newRow.innerHTML = `
                <td><input type="text" name="productName[]" list="products" autocomplete="off"></td>
                <td><input type="number" name="quantity[]" autocomplete="off"></td>
                <td></td>
                <td><button type="button" class="sales__row--remove">Remove</button></td>
            `;
        }

        tbody.appendChild(newRow);

        newRow.querySelector(".sales__row--remove").addEventListener("click", function() {
            tbody.removeChild(newRow);
        });
    });
});

function filterOrders() {
    let searchInput = document.querySelector(".searchBar").value.toLowerCase();
    let cards = document.querySelectorAll(".sales__card");
    let viewAllOrdersButton = document.querySelector(".button__container");

    if (searchInput === "") {
        cards.forEach(card => {
            card.style.display = "";
        });
        viewAllOrdersButton.style.display = "flex";

    } else {
        viewAllOrdersButton.style.display = "none";

        cards.forEach(card => {
            let customerNameElement = card.querySelector("h4");

            if (customerNameElement) {
                let customerName = customerNameElement.innerText.toLowerCase();
                if (customerName.includes(searchInput)) {
                    card.style.display = "";
                } else {
                    card.style.display = "none";
                }
            } else {
                card.style.display = "none";
            }
        });
    }
}
