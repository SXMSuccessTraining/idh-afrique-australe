let selectedColor = null;
let selectedCategorie = null;
let idhData = null;

// === Chargement des données IDH ===
fetch('data/idh_data.json')
  .then(res => res.json())
  .then(data => {
    idhData = data;
  });

// === Gestion de la sélection des pastilles ===
document.querySelectorAll('.pastille').forEach(pastille => {
  pastille.addEventListener('click', () => {
    selectedColor = getComputedStyle(pastille).backgroundColor;
    selectedCategorie = pastille.dataset.categorie;

    // Feedback visuel sur la pastille
    document.querySelectorAll('.pastille').forEach(p => p.classList.remove('selected'));
    pastille.classList.add('selected');

    // Affichage sous la carte
    document.getElementById('selection').textContent = `Pastille sélectionnée : ${selectedCategorie}`;
    document.getElementById('feedback').textContent = "";
  });
});

// === Une fois que le SVG est chargé ===
const svgObject = document.getElementById('carte');

svgObject.addEventListener('load', () => {
  const svgDoc = svgObject.contentDocument;
  const paths = svgDoc.querySelectorAll('path');

  paths.forEach(path => {
    path.style.cursor = 'pointer';

    path.addEventListener('click', () => {
      const countryName = path.getAttribute('id') || path.getAttribute('name');

      if (!countryName) {
        document.getElementById('feedback').textContent = "⚠️ Ce pays n’a pas d’identifiant utilisable.";
        document.getElementById('feedback').style.color = "orange";
        return;
      }

      if (!idhData || !idhData[countryName]) {
        document.getElementById('feedback').textContent = `❌ ${countryName} : non reconnu dans les données.`;
        document.getElementById('feedback').style.color = "orange";
        return;
      }

      if (!selectedCategorie) {
        document.getElementById('feedback').textContent = "🖱️ Clique d’abord sur une pastille.";
        document.getElementById('feedback').style.color = "blue";
        return;
      }

      const bonneCategorie = idhData[countryName].categorie;
      const nom_fr = idhData[countryName].nom_fr;

      if (selectedCategorie === bonneCategorie) {
        path.style.fill = selectedColor;
        document.getElementById('feedback').textContent = `✅ Bravo ! ${nom_fr} est bien en ${bonneCategorie}`;
        document.getElementById('feedback').style.color = "green";
      } else {
        document.getElementById('feedback').textContent = `❌ Mauvaise réponse pour ${nom_fr}.`;
        document.getElementById('feedback').style.color = "red";
      }
    });
  });
});
