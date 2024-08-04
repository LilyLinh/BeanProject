document.querySelectorAll('.delete-form').forEach(form => {
    form.addEventListener('submit', function(event) {
        event.preventDefault();
        fetch(this.action, {
            method: 'POST',
            body: new URLSearchParams(new FormData(this))
        }).then(response => {
            if (response.ok) {
                location.reload();
            }
        });
    });
});

document.addEventListener('DOMContentLoaded', () => {
    const cartItemsContainer = document.getElementById('cart-items');
    let cart = localStorage.getItem('cart');
    if (cart) {
        cart = JSON.parse(cart);
    } else {
        cart = [];
    }

    if (cart.length === 0) {
        cartItemsContainer.innerHTML = '<p>Your cart is empty.</p>';
    } else {
        cart.forEach(item => {
            const itemDiv = document.createElement('div');
            itemDiv.className = 'cart-item';
            itemDiv.innerHTML = `
                <h3>${item.item}</h3>
                <p>Price: €${item.price}</p>
                <p>Quantity: ${item.quantity}</p>
                <p>Total: €${(item.price * item.quantity).toFixed(2)}</p>
            `;
            cartItemsContainer.appendChild(itemDiv);
        });
    }
});