// Main JavaScript for Crafty E-commerce

// Helper function to show toast notifications
function showToast(message, type = 'success') {
    const toast = document.createElement('div');
    toast.className = `toast align-items-center text-white bg-${type} border-0 position-fixed bottom-0 end-0 m-3`;
    toast.setAttribute('role', 'alert');
    toast.setAttribute('aria-live', 'assertive');
    toast.setAttribute('aria-atomic', 'true');
    
    toast.innerHTML = `
        <div class="d-flex">
            <div class="toast-body">
                ${message}
            </div>
            <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast" aria-label="Close"></button>
        </div>
    `;
    
    document.body.appendChild(toast);
    const bsToast = new bootstrap.Toast(toast);
    bsToast.show();
    
    // Remove toast after it's hidden
    toast.addEventListener('hidden.bs.toast', function() {
        document.body.removeChild(toast);
    });
}

// Function to show a prominent alert when an artist tries to add their own product
function showArtistAlert() {
    // Create a modal alert for artist restriction
    const modalElement = document.createElement('div');
    modalElement.className = 'modal fade';
    modalElement.id = 'artistRestrictionModal';
    modalElement.setAttribute('tabindex', '-1');
    modalElement.setAttribute('aria-labelledby', 'artistRestrictionModalLabel');
    modalElement.setAttribute('aria-hidden', 'true');
    
    modalElement.innerHTML = `
        <div class="modal-dialog modal-dialog-centered">
            <div class="modal-content">
                <div class="modal-header bg-warning">
                    <h5 class="modal-title" id="artistRestrictionModalLabel">
                        <i class="fas fa-exclamation-triangle me-2"></i> Artist Restriction
                    </h5>
                    <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
                </div>
                <div class="modal-body">
                    <p class="mb-0">As an artist, you cannot add your own products to your shopping cart. This is to maintain the integrity of the marketplace.</p>
                </div>
                <div class="modal-footer">
                    <button type="button" class="btn btn-primary" data-bs-dismiss="modal">I understand</button>
                </div>
            </div>
        </div>
    `;
    
    document.body.appendChild(modalElement);
    
    // Show the modal
    const modal = new bootstrap.Modal(modalElement);
    modal.show();
    
    // Remove the modal from DOM after it's hidden
    modalElement.addEventListener('hidden.bs.modal', function() {
        document.body.removeChild(modalElement);
    });
}

document.addEventListener('DOMContentLoaded', function() {
    // Product image gallery
    const mainImage = document.getElementById('main-product-image');
    const thumbnails = document.querySelectorAll('.product-thumbnail');
    
    if (thumbnails.length > 0) {
        thumbnails.forEach(thumbnail => {
            thumbnail.addEventListener('click', function() {
                // Update main image
                mainImage.src = this.getAttribute('data-image');
                
                // Update active state
                thumbnails.forEach(thumb => thumb.classList.remove('active'));
                this.classList.add('active');
            });
        });
    }
    
    // Quantity input controls
    const quantityInputs = document.querySelectorAll('.quantity-input');
    
    if (quantityInputs.length > 0) {
        quantityInputs.forEach(input => {
            const decrementBtn = input.previousElementSibling;
            const incrementBtn = input.nextElementSibling;
            
            decrementBtn.addEventListener('click', function() {
                if (input.value > 1) {
                    input.value = parseInt(input.value) - 1;
                }
            });
            
            incrementBtn.addEventListener('click', function() {
                input.value = parseInt(input.value) + 1;
            });
        });
    }
    
    // AJAX cart functionality
    const addToCartForms = document.querySelectorAll('.add-to-cart-form');
    
    if (addToCartForms.length > 0) {
        addToCartForms.forEach(form => {
            form.addEventListener('submit', function(e) {
                e.preventDefault();
                
                const formData = new FormData(this);
                const url = this.getAttribute('action');
                
                fetch(url, {
                    method: 'POST',
                    body: formData,
                    headers: {
                        'X-Requested-With': 'XMLHttpRequest',
                    },
                    credentials: 'same-origin'
                })
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        // Update cart count
                        const cartCount = document.querySelector('.cart-count');
                        if (cartCount) {
                            cartCount.textContent = data.total_items;
                        }
                        
                        // Show success message
                        showToast('Product added to cart successfully!', 'success');
                    } else if (data.message) {
                        // Show error message if there's a message from the server
                        showToast(data.message, 'danger');
                        
                        // If this is an artist trying to add their own product, show a more prominent alert
                        if (data.message.includes('own products')) {
                            showArtistAlert();
                        }
                    }
                })
                .catch(error => console.error('Error:', error));
            });
        });
    }
    
    // RTL support for Arabic
    const htmlElement = document.documentElement;
    if (htmlElement.lang === 'ar') {
        // Add RTL-specific adjustments if needed
        document.body.classList.add('rtl');
    }
});
