document.addEventListener('DOMContentLoaded', () => {
    // Function to handle "Show More" toggles
    function setupShowMoreToggle(toggleSelector, listSelector, initialVisibleCount) {
        const toggleButton = document.querySelector(toggleSelector);
        if (!toggleButton) return;

        const listItems = document.querySelectorAll(`${listSelector} li`);
        const hiddenItems = Array.from(listItems).slice(initialVisibleCount);

        // Initially hide items beyond the initial count
        hiddenItems.forEach(item => item.style.display = 'none');

        if (hiddenItems.length === 0) {
            // If no hidden items, hide the toggle button
            toggleButton.style.display = 'none';
            return;
        }

        let isExpanded = false;

        toggleButton.addEventListener('click', function() {
            isExpanded = !isExpanded;
            hiddenItems.forEach(item => {
                item.style.display = isExpanded ? 'flex' : 'none'; // Use 'flex' for violation items
            });
            this.querySelector('button').textContent = isExpanded ? '查看較少' : '查看更多';
        });
    }

    // Setup toggles for each section
    setupShowMoreToggle('.violation-more-toggle', '.violation-list-items', 3);
    setupShowMoreToggle('.group-more-toggle', '.group-list-items', 4);
    setupShowMoreToggle('.report-more-toggle', '.report-list-items', 3);

    // Dynamic Score Highlight (Optional: if you want a more complex effect)
    // For now, the CSS animation handles the highlight.
    // If you need JS for score changes or more interactivity, add it here.
});