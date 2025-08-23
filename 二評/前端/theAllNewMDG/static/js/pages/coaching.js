document.addEventListener('DOMContentLoaded', () => {
  const list = document.getElementById('tripList');
  const tabAll  = document.getElementById('tab-all');
  const tabAttn = document.getElementById('tab-attn');

  function setActive(tab){
    [tabAll, tabAttn].forEach(b => {
      b.classList.toggle('is-active', b===tab);
      b.setAttribute('aria-selected', b===tab ? 'true' : 'false');
    });
  }

  tabAll.addEventListener('click', () => {
    setActive(tabAll);
    Array.from(list.children).forEach(row => row.style.display = '');
  });

  tabAttn.addEventListener('click', () => {
    setActive(tabAttn);
    Array.from(list.children).forEach(row => {
      row.style.display = (row.dataset.attn === '1') ? '' : 'none';
    });
  });
});

