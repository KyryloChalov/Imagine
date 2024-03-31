const form = document.querySelector('#form');
// const readme = document.querySelector('#readme');
const launchBtn = document.querySelector('#launch-btn');
const goToFormButton = document.querySelector('#go-to-form-btn');
// const goToReadmeButton = document.querySelector('#go-to-readme-btn');



goToFormButton.addEventListener('click', function (e) {
    e.preventDefault();
    form.scrollIntoView();
});


goToReadmeButton.addEventListener('click', function (e) {
    e.preventDefault();
    form.scrollIntoView();
});


// const launchBtn = document.querySelector('#launch-btn');
// const goToFormButton = document.querySelector('#go-to-three-btn');



// goToFormButton.addEventListener('click', function (e) {
//     e.preventDefault();
//     form.scrollIntoView();
// });
