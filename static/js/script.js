function toggleSteps(){
  const el = document.getElementById('steps');
  if(!el) return;
  el.classList.toggle('hidden');
}

document.querySelectorAll('input[name="text"], input[name="key"]').forEach(inp => {
  inp.addEventListener('input', () => {
    inp.value = inp.value.replace(/[^01]/g, '').slice(0,16);
  });
});
