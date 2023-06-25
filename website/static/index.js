function deleteAd(adId) {
    fetch('/delete-ad', {
        method: 'POST',
        body: JSON.stringify({ adId: adId })
    }).then((_res) => {
        window.location.href = "/ogloszenia";
    });
}
function deleteParticipant(participantId) {
    fetch('/delete-participant', {
        method: 'POST',
        body: JSON.stringify({ participantId: participantId })
    }).then((_res) => {
        window.location.href = "/lista-biegaczy";
    });
}
function toggleCheckboxes() {
    const sendToAllCheckbox = document.getElementById("send_to_all");
    const participantCheckboxes = document.querySelectorAll("[name='selected_participants']");

    if (sendToAllCheckbox.checked) {
      participantCheckboxes.forEach(checkbox => {
        checkbox.checked = true;
      });
    } else {
      participantCheckboxes.forEach(checkbox => {
        checkbox.checked = false;
      });
    }
  }