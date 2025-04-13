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
        document.getElementById('feedback').innerText = Pastille sélectionnée : ${selectedCategory};
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

            // Rechercher l'entrée qui correspond au nom nettoyé
            const pays = Object.values(idhData).find(obj => sanitizeId(obj.nom_fr) === id || sanitizeId(Object.keys(idhData).find(k => id === sanitizeId(k))) === id);
            if (!pays) return;

            el.addEventListener('click', () => {
                if (!selectedColor || !selectedCategory) {
                    document.getElementById('feedback').innerText = "Sélectionne une pastille d'abord.";
                    return;
                }

                el.setAttribute('fill', selectedColor);

                const bonneReponse = pays.categorie;
                const message = (bonneReponse === selectedCategory)
                    ? ✅ Bonne réponse pour ${pays.nom_fr}
                    : ❌ Mauvaise réponse pour ${pays.nom_fr}. Catégorie attendue : ${bonneReponse};

                document.getElementById('feedback').innerText = message;
            });
        });
    });