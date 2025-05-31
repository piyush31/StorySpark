// PWA installation helper
let deferredPrompt;
const installButton = document.createElement('button');
installButton.style.display = 'none';
installButton.classList.add('install-button');
installButton.textContent = 'Install App';

// Listen for the beforeinstallprompt event
window.addEventListener('beforeinstallprompt', (e) => {
  // Prevent Chrome 67 and earlier from automatically showing the prompt
  e.preventDefault();
  // Stash the event so it can be triggered later
  deferredPrompt = e;
  // Update UI to notify the user they can add to home screen
  installButton.style.display = 'block';

  installButton.addEventListener('click', () => {
    // Hide the install button
    installButton.style.display = 'none';
    // Show the install prompt
    deferredPrompt.prompt();
    // Wait for the user to respond to the prompt
    deferredPrompt.userChoice.then((choiceResult) => {
      if (choiceResult.outcome === 'accepted') {
        console.log('User accepted the install prompt');
      } else {
        console.log('User dismissed the install prompt');
      }
      // Clear the saved prompt since it can't be used again
      deferredPrompt = null;
    });
  });
});

// Add the install button to the header after DOM content is loaded
document.addEventListener('DOMContentLoaded', () => {
  const header = document.querySelector('.app-header');
  if (header) {
    header.appendChild(installButton);
  }
});

// Handle installed PWAs
window.addEventListener('appinstalled', (event) => {
  console.log('App was installed', event);
  // Hide the install button after successful installation
  installButton.style.display = 'none';
});

export default {
  deferredPrompt,
  installButton
};
