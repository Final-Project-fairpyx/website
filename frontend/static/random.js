// static/random.js

document.querySelector('.random-button').addEventListener('click', function() {
    // Generate random values for student bids
    const students = document.querySelectorAll('tr');
    students.forEach((studentRow, index) => {
        if (index > 0) {  // Skip header row
            const inputs = studentRow.querySelectorAll('input[type="number"]');
            let total = 1000;
            inputs.forEach((input, i) => {
                if (i === inputs.length - 1) {
                    input.value = total;  // Assign remaining total to last course
                } else {
                    const randomBid = Math.floor(Math.random() * total);
                    input.value = randomBid;
                    total -= randomBid;
                }
            });
        }
    });
});
