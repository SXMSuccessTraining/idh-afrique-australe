let selectedColor = null;
let selectedCategory = null;
let idhData = {};

fetch("/data/idh")
  .then((response) => response.json())
  .then((data) => {
    idhData = data;
  });

document.querySelectorAll(".pastille").forEach((p) => {
  p.addEventListener("click", () => {
    selectedColor = getComputedStyle(p).backgroundColor;
    selectedCategory = p.getAttribute("data-cat");
    document.querySelectorAll(".pastille").forEach((el) =>
      el.classList.remove("selected")
    );
    p.classList.add("selected");
    document.getElementById("feedback").textContent = "";
  });
});

document.querySelectorAll("path").forEach((p) => {
  p.style.cursor = "pointer";
  p.addEventListener("click", () => {
    if (!selectedCategory || !selectedColor) {
      document.getElementById("feedback").textContent =
        "👉 Sélectionne une pastille avant de cliquer sur un pays.";
      document.getElementById("feedback").style.color = "orange";
      return;
    }

    const countryId = p.getAttribute("id");
    const pays = idhData[countryId];

    if (!pays) {
      document.getElementById("feedback").textContent = "Pays non reconnu.";
      return;
    }

    if (pays.categorie === selectedCategory) {
      p.setAttribute("fill", selectedColor);
      document.getElementById("feedback").textContent = `✅ ${pays.nom_fr} : bonne réponse !`;
      document.getElementById("feedback").style.color = "green";
    } else {
      document.getElementById("feedback").textContent = `❌ ${pays.nom_fr} : incorrect.`;
      document.getElementById("feedback").style.color = "red";
    }
  });
});
