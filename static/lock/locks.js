document.addEventListener('DOMContentLoaded', function() {
        const card_holder_id = document.querySelector('#id_card_holder_id');
        card_holder_id.classList.add('form-control');
        card_holder_id.placeholder = 'Card Id';

        const card_holder_name = document.querySelector('#id_card_holder_name');
        card_holder_name.classList.add('form-control');
        card_holder_name.classList.add('mt-3');
        card_holder_name.placeholder = 'Card Id';
});