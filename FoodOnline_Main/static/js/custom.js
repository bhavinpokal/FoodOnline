// Google Maps Autocomplete integration

let autocomplete;

function initAutoComplete() {
    autocomplete = new google.maps.places.Autocomplete(
        document.getElementById('id_address'),
        {
            types: ['geocode', 'establishment'],
            //default in this app is "IN" - add your country code
            componentRestrictions: { 'country': ['in'] },
        })
    // function to specify what should happen when the prediction is clicked
    autocomplete.addListener('place_changed', onPlaceChanged);
}

function onPlaceChanged() {
    var place = autocomplete.getPlace();

    // User did not select the prediction. Reset the input field or alert()
    if (!place.geometry) {
        document.getElementById('id_address').placeholder = "Start typing...";
    }
    else {
        console.log('place name=>', place.name)
    }

    // Get the address components and assign them to the fields
    var geocoder = new google.maps.Geocoder()
    var address = document.getElementById('id_address').value

    geocoder.geocode({ 'address': address }, function (results, status) {
        if (status == google.maps.GeocoderStatus.OK) {
            var latitude = results[0].geometry.location.lat();
            var longitude = results[0].geometry.location.lng();

            $('#id_latitude').val(latitude);
            $('#id_longitude').val(longitude);
            $('#id_address').val(address);
        }
    });

    // Loop through address and assign respective data
    for (let i = 0; i < place.address_components.length; i++) {
        for (let j = 0; j < place.address_components[i].types.length; j++) {
            // Country
            if (place.address_components[i].types[j] == 'country') {
                $('#id_country').val(place.address_components[i].long_name);
            }
            // State
            if (place.address_components[i].types[j] == 'administrative_area_level_1') {
                $('#id_state').val(place.address_components[i].long_name);
            }
            // City
            if (place.address_components[i].types[j] == 'locality') {
                $('#id_city').val(place.address_components[i].long_name);
            }
            // Pincode
            if (place.address_components[i].types[j] == 'postal_code') {
                $('#id_pin_code').val(place.address_components[i].long_name);
            } else {
                $('#id_pin_code').val("");
            }
        }

    }
}

$(document).ready(function () {
    // Increase the cart
    $('.increase-cart').on('click', function (e) {
        e.preventDefault();

        food_id = $(this).attr('data-id');
        url = $(this).attr('data-url');

        $.ajax({
            type: 'GET',
            url: url,
            success: function (response) {
                console.log(response);
                if (response.status == 'login_required') {
                    swal(response.message, '', 'info').then(function () {
                        window.location = '/login';
                    })
                }
                if (response.status == 'Failed') {
                    swal(response.message, '', 'error');
                } else {
                    $('#cart_counter').html(response.cart_counter['cart_count']);
                    $('#qty-' + food_id).html(response.qty);
                    cartAmount(
                        response.cart_amount['subtotal'],
                        response.cart_amount['tax_dict'],
                        response.cart_amount['grand_total']
                    );
                }
            }
        })
    });

    // Decrease the cart
    $('.decrease-cart').on('click', function (e) {
        e.preventDefault();

        cart_id = $(this).attr('id');
        food_id = $(this).attr('data-id');
        url = $(this).attr('data-url');

        $.ajax({
            type: 'GET',
            url: url,
            success: function (response) {
                console.log(response);
                if (response.status == 'login_required') {
                    swal(response.message, '', 'info').then(function () {
                        window.location = '/login';
                    })
                } else if (response.status == 'Failed') {
                    swal(response.message, '', 'error');
                } else {
                    $('#cart_counter').html(response.cart_counter['cart_count']);
                    $('#qty-' + food_id).html(response.qty);
                    cartAmount(
                        response.cart_amount['subtotal'],
                        response.cart_amount['tax_dict'],
                        response.cart_amount['grand_total']
                    );
                    if (window.location.pathname == '/cart/') {
                        removeCartItem(response.qty, cart_id);
                        checkEmptyCart();
                    }
                }
            }
        })
    });

    // Delete the cart item
    $('.delete-cart').on('click', function (e) {
        e.preventDefault();

        cart_id = $(this).attr('data-id');
        url = $(this).attr('data-url');

        $.ajax({
            type: 'GET',
            url: url,
            success: function (response) {
                console.log(response);
                if (response.status == 'Failed') {
                    swal(response.message, '', 'error');
                } else {
                    $('#cart_counter').html(response.cart_counter['cart_count']);
                    swal(response.status, response.message, 'success');
                    cartAmount(
                        response.cart_amount['subtotal'],
                        response.cart_amount['tax_dict'],
                        response.cart_amount['grand_total']
                    );
                    removeCartItem(0, cart_id);
                    checkEmptyCart();
                }
            }
        })
    });

    // Display quantity in template between + and - buttons
    $('.item-qty').each(function () {
        var the_id = $(this).attr('id');
        var qty = $(this).attr('data-qty');
        $('#' + the_id).html(qty);
    });

    // Remove cart element if qty = 0
    function removeCartItem(cartItemQty, cart_id) {
        if (cartItemQty <= 0) {
            document.getElementById("cart-item-" + cart_id).remove()
        }
    }

    // Check if cart is empty
    function checkEmptyCart() {
        var cart_counter = document.getElementById("cart_counter").innerHTML
        if (cart_counter == 0) {
            document.getElementById("empty-cart").style.display = "block";
        }
    }

    // Cart amount
    function cartAmount(subtotal, tax_dict, grand_total) {
        if (window.location.pathname == '/cart/') {
            $('#subtotal').html(subtotal);
            $('#total').html(grand_total);

            for (const key1 in tax_dict) {
                for (const key2 in tax_dict[key1]) {
                    $('#tax-' + key1).html(tax_dict[key1][key2])
                }
            }
        }
    }

    // Add Business Hours
    $('.add-hour').on('click', function (e) {
        e.preventDefault();
        var day = document.getElementById('id_day').value
        var from_hour = document.getElementById('id_from_hour').value
        var to_hour = document.getElementById('id_to_hour').value
        var is_closed = document.getElementById('id_is_closed').checked
        var csrf_token = $('input[name=csrfmiddlewaretoken]').val()
        var url = document.getElementById('add-hour-url').value

        if (is_closed) {
            is_closed = 'True'
            condition = 'day != ""'
        } else {
            is_closed = 'False'
            condition = "day!='' && from_hour!='' && to_hour!=''"
        }
        if (eval(condition)) {
            $.ajax({
                type: 'POST',
                url: url,
                data: {
                    'day': day,
                    'from_hour': from_hour,
                    'to_hour': to_hour,
                    'is_closed': is_closed,
                    'csrfmiddlewaretoken': csrf_token
                },
                success: function (response) {
                    if (response.status == 'success') {
                        if (response.is_closed == 'Closed') {
                            html = '<li class="li-hover" id="hour-' + response.id + '"><div class="open-close-time" style="padding-right:40px;"><div class="day-sec" style="width:200px; margin-left:40px; padding-right: 10px;"><span>' + response.day + '</span></div><div class="time-sec" style="width:300px; margin-right:50px; padding-left: 10px;"><span class="option-label" style="margin: 0 20px;">to</span></div><div class="close-time" style="padding-left: 10px !important;"><span style="color: #c52828; float: none; font-size: 13.97px; font-weight: 700; opacity: 1; padding: 0;">Closed</span></div><a href="#" class="remove-hour" data-url="/vendor/opening_hours/remove/' + response.id + '/"><i class="icon-delete"></i></a></div></li>'
                        } else {
                            html = '<li class="li-hover" id="hour-' + response.id + '"><div class="open-close-time opening-time" style="padding-right:40px;"><div class="day-sec" style="width:200px; margin-left:40px; padding-right: 10px;"><span>' + response.day + '</span></div><div class="time-sec" style="width:300px; margin-right:50px; padding-left: 10px;">' + response.from_hour + '<span class="option-label" style="margin: 0 20px;">to</span>' + response.to_hour + '</div><div class="close-time" style="padding-left: 10px !important;"><span style="color: #c52828; float: none; font-size: 13.97px; font-weight: 700; opacity: 1; padding: 0;">Closed</span></div><a href="#" class="remove-hour" data-url="/vendor/opening_hours/remove/' + response.id + '/"><i class="icon-delete"></i></a></div></li>'
                        }
                        $('.opening-hours').append(html);
                        document.getElementById('opening-hours').reset();
                    } else {
                        swal(response.message, '', 'error')
                    }
                }
            })
        } else {
            swal('Please fill all fields', '', 'info')
        }
    });

    // Remove Business Hours
    $('.remove-hour').on('click', function (e) {
        e.preventDefault();
        url = $(this).attr('data-url')

        $.ajax({
            type: 'GET',
            url: url,
            success: function (response) {
                if (response.status == 'success') {
                    document.getElementById('hour-' + response.id).remove();
                }
            }
        })
    })
});