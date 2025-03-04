// JavaScript to handle "View on Map" button clicks
document.querySelectorAll('.view-on-map').forEach(button => {
    button.addEventListener('click', () => {
      const lat = button.getAttribute('data-lat');
      const lon = button.getAttribute('data-lon');
  
      console.log("Latitude:", lat, "Longitude:", lon); // Debugging
  
      if (lat && lon) {
        window.location.href = `/map?lat=${lat}&lon=${lon}`;
      } else {
        alert("Location data is missing!");
      }
    });
  });