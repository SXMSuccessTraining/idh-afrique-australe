let selectedColor = null;
let selectedCategory = null;

// Récupère la palette de couleurs
document.querySelectorAll('.pastille').forEach(pastille => {
    pastille.addEventListener('click', () => {
        selectedColor = pastille.style.backgroundColor;
        selectedCategory = pastille.dataset.cat;
        document.getElementById('feedback').innerText = `Pastille sélectionnée : ${selectedCategory}`;
    });
});

// Charge les vraies données IDH
let idhData = {};
fetch('/data/idh')
    .then(response => response.json())
    .then(data => {
        idhData = data;

        // Ajoute les écouteurs sur les pays une fois les données chargées
        document.querySelectorAll('#map path, #map circle').forEach(el => {
            const desc = el.querySelector('desc');
            if (!desc) return;

            const id = desc.textContent;

            el.addEventListener('click', () => {
                if (!selectedColor || !selectedCategory) {
                    document.getElementById('feedback').innerText = "Sélectionne une pastille d'abord.";
                    return;
                }

                el.setAttribute('fill', selectedColor);

                const bonneReponse = idhData[id]?.categorie;
                const nom_fr = idhData[id]?.nom_fr || id;

                const message = (bonneReponse === selectedCategory)
                    ? `✅ Bonne réponse pour ${nom_fr}`
                    : `❌ Mauvaise réponse pour ${nom_fr}. Catégorie attendue : ${bonneReponse}`;

                document.getElementById('feedback').innerText = message;
            });
        });
    });
