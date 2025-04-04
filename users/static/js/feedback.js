function rateService(rating) {
    let stars = document.querySelectorAll('.star-rating .fa-star');
    stars.forEach((star, index) => {
        if (index < rating) {
            star.classList.add('selected');
        } else {
            star.classList.remove('selected');
        }
    });
    document.getElementById('ratingInput').value = rating;
}

document.getElementById('feedbackForm').addEventListener('submit', function(e) {
    const rating = document.getElementById('ratingInput').value;
    const feedback = document.querySelector('textarea').value;
    
    if (!rating || !feedback) {
        e.preventDefault();
        alert("Please fill out all fields and select a rating.");
    }
});