document.addEventListener("DOMContentLoaded", () => {
  const flashWrap = document.getElementById("flash-wrap");
  if (flashWrap) {
    setTimeout(() => {
      flashWrap.style.transition = "opacity 0.4s ease";
      flashWrap.style.opacity = "0";
      setTimeout(() => flashWrap.remove(), 400);
    }, 4000);
  }
});
