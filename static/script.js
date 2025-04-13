let selectedColor = null;
let selectedCategory = null;

// Fonction pour "nettoyer" un nom comme le fait sanitize_id en Python
function sanitizeId(str) {
    return str.replace(/[^a-zA-Z0-9_-]/g, '_');
}

// Sélection d'une pastille
document.querySelectorAll('.pastille').forEach(pastille => {
    pastille.addEventListener('click', () => {
        selectedColor = pastille.style.backgroundColor;
        selectedCategory = pastille.dataset.cat;
        document.getElementById('feedback').innerText = `Pastille sélectionnée : ${selectedCategory}`;
    });
});

// Données IDH depuis le backend
fetch('/data/idh')
    .then(response => response.json())
    .then(data => {
        const idhData = data;

        // Sélectionne tous les pays (paths et cercles comme Seychelles)
        document.querySelectorAll("path, circle").forEach(el => {
            const id = el.id;

            // Rechercher l'entrée correspondante
            const pays = Object.entries(idhData).find(([key, value]) =>
                sanitizeId(key) === id || sanitizeId(value.nom_fr) === id
            );

            if (!pays) return;

            const [code, info] = pays;

            el.addEventListener('click', () => {
                if (!selectedColor || !selectedCategory) {
                    document.getElementById('feedback').innerText = "Sélectionne une pastille d'abord.";
                    return;
                }

                el.setAttribute('fill', selectedColor);

                const bonneReponse = info.categorie;
                const message = (bonneReponse === selectedCategory)
                    ? `✅ Bonne réponse pour ${info.nom_fr}`
                    : `❌ Mauvaise réponse pour ${info.nom_fr}. Catégorie attendue : ${bonneReponse}`;

                document.getElementById('feedback').innerText = message;
            });
        });
    });
