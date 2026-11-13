# Importing into Google AI Studio

Use the repository's web-app root, not the Python plugin folder.

The root entry points are:
- `package.json`
- `index.html`
- `src/main.jsx`
- `src/App.jsx`
- `src/styles.css`

The app is a Vite + React project. If AI Studio asks for an app type, choose a web application. Do not import only `plugins/wan2gp-gentleman-studio`; that folder is a WanGP plugin, not the website.

The app shell is ready for UI iteration. The Generate action intentionally reports that the private WanGP worker is not connected yet. Authentication, the GPU worker, and YouTube OAuth must be implemented before production deployment.
