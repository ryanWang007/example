// JavaScript 只负责删除前的确认；CRUD 的实际工作在 app.py。
document.querySelectorAll('[data-confirm-delete]').forEach((form) => {
  form.addEventListener('submit', (event) => {
    if (!window.confirm('确定删除这套穿搭吗？删除后无法恢复。')) {
      event.preventDefault();
    }
  });
});
