// Apprecity Accessories Store - Dynamic Cart Handlers
document.addEventListener("DOMContentLoaded", () => {
    updateCartBadge();

    // Event listener for dynamic adding
    document.body.addEventListener("click", (e) => {
        if (e.target && e.target.classList.contains("ajax-add-to-cart")) {
            e.preventDefault();
            const productId = e.target.getAttribute("data-id");
            const quantity = document.getElementById("quantity-input") ? document.getElementById("quantity-input").value : 1;
            addToCart(productId, quantity);
        }
    });
});

// Get cookie for Django CSRF
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

// Update cart counter badge in navigation
function updateCartBadge() {
    fetch("/cart/api/count/")
        .then(response => response.json())
        .then(data => {
            const badge = document.getElementById("cart-badge");
            if (badge) {
                badge.innerText = data.count;
                // Add minor scale animation
                badge.style.transform = "scale(1.3)";
                setTimeout(() => {
                    badge.style.transform = "scale(1)";
                }, 300);
            }
        })
        .catch(err => console.log("Failed to fetch cart count:", err));
}

// Add item to cart dynamically
function addToCart(productId, quantity = 1) {
    const csrftoken = getCookie('csrftoken');
    
    fetch(`/cart/api/add/${productId}/`, {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
            "X-CSRFToken": csrftoken
        },
        body: JSON.stringify({ quantity: parseInt(quantity) })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            updateCartBadge();
            showNotification(data.message, "success");
        } else {
            showNotification(data.message || "عذراً، حدث خطأ ما", "error");
        }
    })
    .catch(err => {
        console.error("Error adding to cart:", err);
        showNotification("حدث خطأ في الشبكة، يرجى المحاولة لاحقاً", "error");
    });
}

// Show premium custom notification
function showNotification(message, type = "success") {
    // Create element
    const notification = document.createElement("div");
    notification.className = `alert alert-${type}`;
    notification.style.position = "fixed";
    notification.style.bottom = "20px";
    notification.style.left = "20px";
    notification.style.zIndex = "9999";
    notification.style.minWidth = "300px";
    notification.style.marginBottom = "0";
    notification.style.boxShadow = "0 10px 25px rgba(0,0,0,0.5)";
    notification.style.animation = "slideIn 0.3s ease-out forwards";

    // CSS Keyframe animation
    if (!document.getElementById("notification-animation-style")) {
        const style = document.createElement("style");
        style.id = "notification-animation-style";
        style.innerHTML = `
            @keyframes slideIn {
                from { transform: translateY(100px); opacity: 0; }
                to { transform: translateY(0); opacity: 1; }
            }
            @keyframes slideOut {
                from { transform: translateY(0); opacity: 1; }
                to { transform: translateY(100px); opacity: 0; }
            }
        `;
        document.head.appendChild(style);
    }

    notification.innerHTML = `
        <span>${message}</span>
        <button class="close-alert" style="margin-right: 1.5rem;">&times;</button>
    `;

    // Close button event
    notification.querySelector(".close-alert").addEventListener("click", () => {
        notification.remove();
    });

    document.body.appendChild(notification);

    // Auto remove after 4 seconds
    setTimeout(() => {
        notification.style.animation = "slideOut 0.3s ease-in forwards";
        setTimeout(() => {
            notification.remove();
        }, 300);
    }, 4000);
}
