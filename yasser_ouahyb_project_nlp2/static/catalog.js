document.addEventListener("DOMContentLoaded", () => {
    // Check if we are on the page with the catalog
    const catalogGrid = document.getElementById("catalog-grid");
    if (!catalogGrid) return;

    const secteurFilter = document.getElementById("secteur-filter");
    const niveauFilter = document.getElementById("niveau-filter");
    const searchFilter = document.getElementById("search-filter");
    const modal = document.getElementById("formation-modal");
    const closeModalBtn = document.getElementById("close-modal");

    let formations = [];
    let currentLang = document.documentElement.lang || 'fr';

    // Fetch formations data
    fetch('/static/formations.json')
        .then(response => response.json())
        .then(data => {
            formations = data;
            populateFilters();
            renderCatalog(formations);
        })
        .catch(error => {
            console.error("Erreur de chargement des formations:", error);
            catalogGrid.innerHTML = "<p>Impossible de charger le catalogue de formations pour le moment.</p>";
        });

    // Re-render when language changes
    window.addEventListener('languageChanged', (e) => {
        currentLang = e.detail.lang;
        populateFilters();
        filterCatalog();
    });

    function getLocalText(obj) {
        if (!obj) return "";
        if (typeof obj === 'string') return obj; // Handle non-multilingual fields like 'id' or 'duree' (if un-split)
        return obj[currentLang] || obj['fr'] || "";
    }

    function populateFilters() {
        const secteurs = new Set();
        const niveaux = new Set();

        formations.forEach(f => {
            const secteurLoc = getLocalText(f.secteur);
            const niveauLoc = getLocalText(f.niveau);
            if (secteurLoc) secteurs.add(secteurLoc);
            if (niveauLoc) niveaux.add(niveauLoc);
        });

        // Save current selections to keep them if possible
        const currentSecteur = secteurFilter.value;
        const currentNiveau = niveauFilter.value;

        // Reset
        secteurFilter.innerHTML = `<option value="all" data-i18n="filter_secteur_all">${currentLang === 'ar' ? 'كل القطاعات' : 'Tous les secteurs'}</option>`;
        niveauFilter.innerHTML = `<option value="all" data-i18n="filter_niveau_all">${currentLang === 'ar' ? 'كل المستويات' : 'Tous les niveaux'}</option>`;

        // Populate Secteurs
        Array.from(secteurs).sort().forEach(secteur => {
            const option = document.createElement("option");
            option.value = secteur;
            option.textContent = secteur;
            if (secteur === currentSecteur) option.selected = true;
            secteurFilter.appendChild(option);
        });

        // Populate Niveaux
        Array.from(niveaux).sort().forEach(niveau => {
            const option = document.createElement("option");
            option.value = niveau;
            option.textContent = niveau;
            if (niveau === currentNiveau) option.selected = true;
            niveauFilter.appendChild(option);
        });
    }

    function renderCatalog(filteredFormations) {
        catalogGrid.innerHTML = "";

        if (filteredFormations.length === 0) {
            const noResText = currentLang === 'ar' ? 'لا يوجد تكوين يطابق معايير البحث الخاصة بك.' : 'Aucune formation ne correspond à vos critères de recherche.';
            catalogGrid.innerHTML = `<p class='no-results'>${noResText}</p>`;
            return;
        }

        filteredFormations.forEach(formation => {
            const card = document.createElement("div");
            card.className = "formation-card";

            const titre = getLocalText(formation.titre);
            const niveau = getLocalText(formation.niveau);
            const secteur = getLocalText(formation.secteur);
            const duree = typeof formation.duree === 'string' ? formation.duree.split(' / ')[currentLang === 'ar' ? 1 : 0] : getLocalText(formation.duree);
            const btnText = currentLang === 'ar' ? 'عرض التفاصيل' : 'Voir les détails';
            const arrowIcon = currentLang === 'ar' ? 'fa-arrow-left' : 'fa-arrow-right';

            card.innerHTML = `
                <div class="card-badges">
                    <span class="badge badge-niveau">${niveau}</span>
                    <span class="badge badge-secteur">${secteur}</span>
                </div>
                <h4>${titre}</h4>
                <p class="card-duree"><i class="fas fa-clock"></i> ${duree}</p>
                <button class="btn-details" data-id="${formation.id}">${btnText} <i class="fas ${arrowIcon}"></i></button>
            `;
            catalogGrid.appendChild(card);
        });

        // Add event listeners to the new buttons
        document.querySelectorAll('.btn-details').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const id = e.currentTarget.getAttribute('data-id');
                const formation = formations.find(f => f.id === id);
                if (formation) {
                    openModal(formation);
                }
            });
        });
    }

    function filterCatalog() {
        const secteurValue = secteurFilter.value;
        const niveauValue = niveauFilter.value;
        const searchValue = searchFilter.value.toLowerCase();

        const filtered = formations.filter(f => {
            const fSecteur = getLocalText(f.secteur);
            const fNiveau = getLocalText(f.niveau);
            const fTitre = getLocalText(f.titre).toLowerCase();

            const matchSecteur = secteurValue === "all" || fSecteur === secteurValue;
            const matchNiveau = niveauValue === "all" || fNiveau === niveauValue;
            const matchSearch = fTitre.includes(searchValue) || fSecteur.toLowerCase().includes(searchValue);
            return matchSecteur && matchNiveau && matchSearch;
        });

        renderCatalog(filtered);
    }

    // Event Listeners for Filters
    secteurFilter.addEventListener("change", filterCatalog);
    niveauFilter.addEventListener("change", filterCatalog);
    searchFilter.addEventListener("input", filterCatalog);

    // Modal logic
    function openModal(formation) {
        document.getElementById("modal-niveau").textContent = getLocalText(formation.niveau);
        document.getElementById("modal-secteur").textContent = getLocalText(formation.secteur);
        document.getElementById("modal-title").textContent = getLocalText(formation.titre);

        const duree = typeof formation.duree === 'string' ? formation.duree.split(' / ')[currentLang === 'ar' ? 1 : 0] : getLocalText(formation.duree);
        document.getElementById("modal-duree").textContent = duree;

        document.getElementById("modal-programme").innerHTML = getLocalText(formation.programme);

        const debouchesList = document.getElementById("modal-debouches");
        debouchesList.innerHTML = "";

        const debouchesArray = formation.debouches[currentLang] || formation.debouches['fr'] || [];
        debouchesArray.forEach(d => {
            const li = document.createElement("li");
            li.innerHTML = `<i class="fas fa-check-circle"></i> ${d}`;
            debouchesList.appendChild(li);
        });

        modal.classList.add("active");
        document.body.style.overflow = "hidden"; // Prevent scrolling
    }

    function closeModal() {
        modal.classList.remove("active");
        document.body.style.overflow = "";
    }

    if (closeModalBtn && modal) {
        closeModalBtn.addEventListener("click", closeModal);

        // Close modal when clicking completely outside the modal content
        modal.addEventListener("click", (e) => {
            if (e.target === modal) {
                closeModal();
            }
        });
    }
});
