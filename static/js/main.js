function flash(btn, text) {
  const orig = btn.textContent;
  btn.textContent = text;
  btn.classList.add("done");
  setTimeout(() => { btn.textContent = orig; btn.classList.remove("done"); }, 1500);
}
document.querySelectorAll("button.copy").forEach((btn) => {
  btn.addEventListener("click", async () => {
    const text = btn.dataset.copyTarget
      ? document.getElementById(btn.dataset.copyTarget).textContent
      : btn.dataset.copy;
    try {
      await navigator.clipboard.writeText(text);
      flash(btn, "copied");
    } catch {
      flash(btn, "failed");
    }
  });
});
