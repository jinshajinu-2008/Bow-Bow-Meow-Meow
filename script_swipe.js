document.addEventListener('DOMContentLoaded', () => {
    const cardContainer = document.getElementById('card-container');
    const btnLike = document.getElementById('btn-like');
    const btnPass = document.getElementById('btn-pass');
    
    let pets = [];
    let currentPetIndex = 0;

    // Check login
    const user_id = localStorage.getItem('user_id');
    if (!user_id) {
        alert("Please login first!");
        window.location.href = 'match_maker.html';
        return;
    }

    // Fetch Pets
    fetch(`http://127.0.0.1:5000/pets?user_id=${user_id}`)
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                pets = data.pets;
                renderCard();
            }
        })
        .catch(err => console.error(err));

    function renderCard() {
        cardContainer.innerHTML = '';
        
        if (currentPetIndex >= pets.length) {
            cardContainer.innerHTML = '<div class="no-more-pets"><h2>No more pets nearby!</h2></div>';
            return;
        }

        const pet = pets[currentPetIndex];
        const card = document.createElement('div');
        card.className = 'card';
        card.style.backgroundImage = `url('${pet.image_url}')`;
        
        card.innerHTML = `
            <div class="card-info">
                <h2>${pet.name}, ${pet.age}</h2>
                <p>${pet.breed} • ${pet.location}</p>
            </div>
        `;
        
        cardContainer.appendChild(card);
    }

    function handleSwipe(status) {
        if (currentPetIndex >= pets.length) return;
        
        const pet = pets[currentPetIndex];
        
        fetch('http://127.0.0.1:5000/swipe', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                user_id: user_id,
                pet_id: pet.id,
                status: status
            })
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                if (data.match) {
                    alert(`It's a Match! You and ${pet.name} liked each other!`);
                }
                currentPetIndex++;
                renderCard();
            }
        });
    }

    btnLike.addEventListener('click', () => handleSwipe('liked'));
    btnPass.addEventListener('click', () => handleSwipe('passed'));
});
