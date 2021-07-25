let burger = document.getElementById('burger');
let nav = document.getElementById('nav-links');

burger.addEventListener('click', () => {
    nav.classList.toggle('nav-active');
});