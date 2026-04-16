const buttons = document.querySelectorAll(".button");

buttons.forEach((button) => {
  button.addEventListener("click", () => {
    button.animate(
      [
        { transform: "translateY(0px)" },
        { transform: "translateY(-2px)" },
        { transform: "translateY(0px)" },
      ],
      {
        duration: 220,
        easing: "ease-out",
      }
    );
  });
});
