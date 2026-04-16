const buttons = document.querySelectorAll(".button");
const dialogueInput = document.querySelector("#dialogue-input");
const analyzeButton = document.querySelector("#analyze-btn");
const resetButton = document.querySelector("#reset-btn");
const importStatus = document.querySelector("#import-status");
const filesCount = document.querySelector("#files-count");
const pipelineState = document.querySelector("#pipeline-state");
const nextStep = document.querySelector("#next-step");
const outputDetails = document.querySelector("#output-details");

let selectedFiles = [];

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

dialogueInput.addEventListener("change", () => {
  selectedFiles = Array.from(dialogueInput.files || []);
  const fileCount = selectedFiles.length;
  importStatus.textContent = fileCount
    ? `${fileCount} fichier${fileCount > 1 ? "s" : ""} prêt${fileCount > 1 ? "s" : ""} pour l'analyse.`
    : "Aucun dossier importé pour le moment.";
  filesCount.textContent = `${fileCount} fichier${fileCount > 1 ? "s" : ""}`;
  pipelineState.textContent = fileCount ? "Dossier prêt pour le pipeline." : "En attente d’import.";
  nextStep.textContent = fileCount
    ? "Lancer l’analyse du pipeline Solena."
    : "Importer un dossier de dialogues.";
  outputDetails.textContent = fileCount
    ? "Solena peut maintenant lire le GPS, la gouvernance et le pipeline guide avant de traiter les dialogues."
    : "Le système attend une source de dialogues pour démarrer.";
});

analyzeButton.addEventListener("click", () => {
  const fileCount = selectedFiles.length;
  const hasFiles = fileCount > 0;

  pipelineState.textContent = hasFiles ? "Analyse simulée en cours." : "Aucun dossier à analyser.";
  nextStep.textContent = hasFiles
    ? "Lire project_gps.json puis pipeline_guide.json."
    : "Importer un dossier avant de lancer l’analyse.";
  outputDetails.innerHTML = hasFiles
    ? `<strong>Pipeline chargé.</strong><br>${fileCount} fichier${fileCount > 1 ? "s" : ""} détecté${fileCount > 1 ? "s" : ""}.<br>
      Étapes: GPS -> gouvernance -> raffinage -> risques -> version -> lab -> initialisation.`
    : "Aucune analyse possible tant qu’aucun dossier n’a été importé.";

  analyzeButton.animate(
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

resetButton.addEventListener("click", () => {
  dialogueInput.value = "";
  selectedFiles = [];
  importStatus.textContent = "Aucun dossier importé pour le moment.";
  filesCount.textContent = "0 fichier";
  pipelineState.textContent = "En attente d’import.";
  nextStep.textContent = "Importer un dossier de dialogues.";
  outputDetails.textContent = "Le système attend une source de dialogues pour démarrer.";
});
