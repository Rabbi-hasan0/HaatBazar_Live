
$(document).ready(function () {
    // console.log("cart_operation.js LOADED");
    // document.querySelectorAll('.product-qty-box').forEach(box => {
    document.querySelectorAll('.product-qty-box, .pocket-product-qty').forEach(box => {
        const incrementBtn = box.querySelector('.increment');
        const decrementBtn = box.querySelector('.decrement');
        const qtyInput = box.querySelector('.cart_qty');

        incrementBtn.addEventListener('click', () => {
            let currentValue = parseInt(qtyInput.value) || 0;
            const maxValue = parseInt(qtyInput.max) || 50;
            if (currentValue < maxValue) {
                qtyInput.value = currentValue + 1;
                updateCart(qtyInput);
            }
        });

        decrementBtn.addEventListener('click', () => {
            let currentValue = parseInt(qtyInput.value) || 0;
            const minValue = parseInt(qtyInput.min) || 0;
            if (currentValue > minValue) {
                qtyInput.value = currentValue - 1;
                updateCart(qtyInput);
            }
        });
    });

    $(document).on('click', '.add_to_cart_btn', function (e) {
        e.preventDefault();
        const parentRow = $(this).parent().parent();
        
        if (parentRow.length) {
            // const qtyInput = document.getElementById('cart_qty');
            const qtyInput = parentRow.find('.cart_qty');

            if (qtyInput.length) {
                let currentValue = parseInt(qtyInput.val()) || 0;
                if (currentValue === 0) {
                    // qtyInput.value = 1;
                    qtyInput.val(1);
                } else {
                    // qtyInput.value = 0;
                    qtyInput.val(0);
                }        
                updateCart(qtyInput);
            }
        }
    });

    document.querySelectorAll('button[id^="delete_cart__"]').forEach(deleteLink => {
        deleteLink.onclick = function (event) {
            event.preventDefault();
            const parentRow = this.closest('tr');
            // console.log(parentRow);

            if (parentRow) {
                // console.log('Parent Row:', parentRow);
                // parentRow.remove();

                const qtyInput = parentRow.querySelector('.cart_qty');

                let currentValue = parseInt(qtyInput.value) || 0;
                if (currentValue === 0) {
                    qtyInput.value = 1;
                } else {
                    qtyInput.value = 0;
                }        
                updateCart(qtyInput);
            }
        };
    });

    function updateCart(qtyInput) {
        const productId = $(qtyInput).data('product-id');
        const newQty = $(qtyInput).val();

        $.ajax({
            url: '/backend/add-or-update-cart/',
            type: 'POST',
            // updateCart function-er bhitore data section-ta eibabe likho
            data: {
                'product_id': productId,
                'quantity': newQty,
                'csrfmiddlewaretoken': document.querySelector('[name=csrfmiddlewaretoken]').value,
            },
            success: function (response) {
                console.log(response);

                if (!response.is_authenticated) {
                    const currentUrl = window.location.href;
                    const loginUrl = `/backend/login/?next=${encodeURIComponent(currentUrl)}`;
                    
                    window.location.href = loginUrl;
                    return;
                } else if (response.status === 'success') {
                    // Update Cart Quantity
                    var itemQuantityElements = document.getElementsByClassName('cart_qty__' + productId);
                    Array.from(itemQuantityElements).forEach(function (itemQuantityElement) {
                        itemQuantityElement.value = newQty;
                    });
                    // Update Cart Quantity
                    
                    // Update Cart Item
                    if (response.isRemoved) {
                        var cartItemElements = document.getElementsByClassName('cart_item__' + productId);
                        Array.from(cartItemElements).forEach(function (cartItemElement) {
                            cartItemElement.remove();
                        });
                    } else {
                        var itemPriceElements = document.getElementsByClassName('total_price__' + productId);
                        Array.from(itemPriceElements).forEach(function (itemPriceElement) {
                            itemPriceElement.innerHTML = `${response.item_price.toFixed(2)}`;
                        });
                    }
                    // Update Cart Item

                    // Agere code-er jaygay eita likhun:
                    var addButton = document.querySelector(`.add_to_cart_btn[data-product-id="${productId}"]`);
                    if (addButton) {
                        if (addButton) {
                            if (newQty > 0) {
                                addButton.innerText = 'Remove from Cart';
                            } else {
                                addButton.innerText = 'Add to Cart';
                            }
                        }
                        
                        if (newQty > 0) { 
                            addButton.innerText = 'Remove from Cart'; 
                        } else { 
                            addButton.innerText = 'Add to Cart'; 
                        }
                    }

                    // Update Cart Amounts
                    var subTotalAmountElements = document.getElementsByClassName('sub_total_amount');
                    Array.from(subTotalAmountElements).forEach(function (subTotalAmountElement) {
                        subTotalAmountElement.innerHTML = `${response.amount_summary.sub_total_amount.toFixed(2)}`;
                    });
                    // var subTotalAmount = document.getElementById('sub_total_amount');
                    // if (subTotalAmount) { subTotalAmount.innerHTML = `${response.amount_summary.sub_total_amount.toFixed(2)}`; }
                    
                    var vatAmount = document.getElementById('total_vat');
                    if (vatAmount) { vatAmount.innerHTML = `${response.amount_summary.total_vat.toFixed(2)}`; }
                    
                    var discountAmount = document.getElementById('total_discount');
                    if (discountAmount) { discountAmount.innerHTML = `${response.amount_summary.total_discount.toFixed(2)}`; }
                    
                    var grandTotalAmount = document.getElementById('grand_total');
                    if (grandTotalAmount) { grandTotalAmount.innerHTML = `${response.amount_summary.grand_total.toFixed(2)}`; }

                    
                    var cartItemCountElements = document.getElementsByClassName('cart_item_quantity');
                    Array.from(cartItemCountElements).forEach(function (cartItemCountElement) {
                        cartItemCountElement.innerHTML = response.cart_item_count;
                    });
                    // var cartItemCount = document.getElementById('cart_item_quantity');
                    // if (cartItemCount) {
                    //     // if (response.cart_item_count > 0) {
                    //         cartItemCount.innerHTML = response.cart_item_count;
                    //     //     cartItemCount.style.display = 'inline-block';
                    //     // } else {
                    //     //     cartItemCount.style.display = 'none';
                    //     // }
                    // }
                    // Update Cart Amounts
                } else {
                    alert('Failed to update the cart: ' + response.message);
                }
            },
            error: function (response) {
                console.error('Error updating cart:', response);
                if (!response.is_authenticated) {
                    const currentUrl = window.location.pathname;
                    const loginUrl = `/backend/login/?next=${encodeURIComponent(currentUrl)}`;
                    
                    window.location.href = loginUrl;
                    return;
                } else {
                    alert('An error occurred while updating the cart.');
                }
            }
        });
    }

    $('.cart_qty').on('change', function () {
        const productId = $(this).data('product-id');
        const newQty = $(this).val();
        updateCart(this);
    });

    // hamburger-menu-show
    // document.getElementById("hamburger-menu-show").addEventListener("click", function () {
    //     const menu = document.getElementById("hamburger-nav-menu");
        
    //     if (menu.classList.contains("show")) {
    //         menu.classList.remove("show");
    //         setTimeout(() => {
    //             menu.style.display = "none"; 
    //         }, 300); 
    //     } else {
    //         menu.style.display = "block";
    //         setTimeout(() => {
    //             menu.classList.add("show");
    //         }, 10); 
    //     }
    // });
});


