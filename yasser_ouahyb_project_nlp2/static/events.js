document.addEventListener('DOMContentLoaded', () => {

    /* ========================================================= */
    /* DYNAMIC CALENDAR ENGINE                                   */
    /* ========================================================= */

    // Get current date for initial display
    const now = new Date();
    let displayYear  = now.getFullYear();
    let displayMonth = now.getMonth() + 1; // 1-indexed

    // Events data — simplified for demo, can be expanded
    const eventDays = {
        '2026-3': [15, 20, 25],   // March 2026
        '2024-3': [15, 20, 25],   // Current March 2024
        '2025-3': [15, 20, 25],
    };

    // Add current month/year to event data if not present
    const currentKey = `${displayYear}-${displayMonth}`;
    if (!eventDays[currentKey]) eventDays[currentKey] = [15, 22, 28];

    const MONTHS_FR = [
        'Janvier', 'Février', 'Mars', 'Avril', 'Mai', 'Juin',
        'Juillet', 'Août', 'Septembre', 'Octobre', 'Novembre', 'Décembre'
    ];

    const calGrid      = document.querySelector('.calendar-grid');
    const currentMonthEl = document.querySelector('.current-month');
    const navBtns      = document.querySelectorAll('.cal-nav-btn');
    const eventCards   = document.querySelectorAll('.event-card');

    function buildCalendar(year, month) {
        // Update header
        currentMonthEl.textContent = `${MONTHS_FR[month - 1].toUpperCase()} ${year}`;

        // First day of target month (0=Sun..6=Sat)
        const firstDayDate = new Date(year, month - 1, 1);
        const dayOfWeek = firstDayDate.getDay(); 
        
        // Convert to Mon-based (0=Mon, 1=Tue... 6=Sun)
        const startOffset = (dayOfWeek === 0) ? 6 : dayOfWeek - 1;

        // Days count
        const daysInMonth = new Date(year, month, 0).getDate();
        const daysInPrevMonth = new Date(year, month - 1, 0).getDate();

        // Event days for this month
        const key = `${year}-${month}`;
        const eventDaysSet = new Set(eventDays[key] || []);

        let html = '';

        // 1. Previous month trailing days
        for (let i = startOffset - 1; i >= 0; i--) {
            const d = daysInPrevMonth - i;
            html += `<div class="cal-day prev-month">${d}</div>`;
        }

        // 2. Current month days
        for (let d = 1; d <= daysInMonth; d++) {
            const hasEvent = eventDaysSet.has(d);
            const isToday = (year === now.getFullYear() && month === (now.getMonth() + 1) && d === now.getDate());
            
            let classes = ['cal-day'];
            if (hasEvent) classes.push('has-event');
            if (isToday) classes.push('today');
            
            html += `<div class="${classes.join(' ')}">${d}</div>`;
        }

        // 3. Next month leading days (fill to 42 cells for 6 rows consistent grid)
        const totalSoFar = startOffset + daysInMonth;
        const nextMonthDays = 42 - totalSoFar;
        for (let d = 1; d <= nextMonthDays; d++) {
            html += `<div class="cal-day next-month">${d}</div>`;
        }

        calGrid.innerHTML = html;
        bindCalDayClicks();
    }

    function bindCalDayClicks() {
        const calDays = document.querySelectorAll('.cal-day');

        calDays.forEach(day => {
            day.addEventListener('click', function () {
                if (this.classList.contains('prev-month') || this.classList.contains('next-month')) return;

                calDays.forEach(d => d.classList.remove('active'));
                this.classList.add('active');

                const clickedDay = this.textContent.trim();
                let foundAny = false;

                eventCards.forEach(card => {
                    if (card.dataset.eventDay === clickedDay) {
                        card.classList.remove('filtered-out');
                        card.classList.add('filtered-in');
                        card.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
                        foundAny = true;
                    } else {
                        card.classList.add('filtered-out');
                        card.classList.remove('filtered-in');
                    }
                });

                // If no event on this day, keep everything visible but dimmed? 
                // Or just show "No events" - for now we blur non-matches.
            });
        });
    }

    function resetFilters() {
        document.querySelectorAll('.cal-day').forEach(d => d.classList.remove('active'));
        eventCards.forEach(card => {
            card.classList.remove('filtered-out', 'filtered-in');
        });
    }

    // Navigation buttons
    if (navBtns.length >= 2) {
        navBtns[0].addEventListener('click', () => {
            displayMonth--;
            if (displayMonth < 1) { displayMonth = 12; displayYear--; }
            buildCalendar(displayYear, displayMonth);
            resetFilters();
        });

        navBtns[1].addEventListener('click', () => {
            displayMonth++;
            if (displayMonth > 12) { displayMonth = 1; displayYear++; }
            buildCalendar(displayYear, displayMonth);
            resetFilters();
        });
    }

    currentMonthEl.addEventListener('click', resetFilters);

    // Initial build
    buildCalendar(displayYear, displayMonth);


    /* ========================================================= */
    /* EVENT REGISTRATION MODAL LOGIC                            */
    /* ========================================================= */
    const eventModal       = document.getElementById('event-registration-modal');
    const closeEventModalBtn = document.getElementById('close-event-modal');
    const formView         = document.getElementById('event-form-view');
    const successView      = document.getElementById('event-success-view');
    const modalEventTitle  = document.getElementById('modal-event-title');
    const eventForm        = document.getElementById('event-registration-form');
    const btnCloseSuccess  = document.getElementById('btn-close-success');

    // Select open buttons dynamically in case they are regenerated
    function bindOpenModalButtons() {
        const openBtns = document.querySelectorAll('.js-btn-inscription');
        openBtns.forEach(btn => {
            btn.onclick = (e) => {
                modalEventTitle.textContent = e.currentTarget.dataset.eventTitle;
                openModal();
            };
        });
    }

    function openModal() {
        eventModal.classList.add('active');
        document.body.style.overflow = 'hidden';
        formView.style.display = 'block';
        successView.style.display = 'none';
        eventForm.reset();
    }

    function closeModal() {
        eventModal.classList.remove('active');
        document.body.style.overflow = '';
    }

    if (closeEventModalBtn) closeEventModalBtn.onclick = closeModal;
    if (btnCloseSuccess) btnCloseSuccess.onclick = closeModal;
    if (eventModal) eventModal.onclick = e => { if (e.target === eventModal) closeModal(); };

    if (eventForm) {
        eventForm.onsubmit = e => {
            e.preventDefault();
            const submitBtn = document.getElementById('btn-submit-event');
            const orig = submitBtn.innerHTML;
            submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Traitement...';
            submitBtn.disabled = true;

            setTimeout(() => {
                submitBtn.innerHTML = orig;
                submitBtn.disabled = false;
                formView.style.display = 'none';
                successView.style.display = 'block';
            }, 1000);
        };
    }
    
    bindOpenModalButtons();
});
