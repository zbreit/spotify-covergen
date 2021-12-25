// Settings
const BACKGROUND_COLOR = "#2f3030";
const CELLS_PER_SIDE = 6;
const NUM_LARGE_CELLS = 2;
const TILT_ANGLE = 15;
const EXTRA_CELLS = TILT_ANGLE == 0 ? 0 : Math.max(1, Math.floor(CELLS_PER_SIDE / 3));
const GAP_SIZE = 10;
const CANVAS_SIZE = 512;
const CELL_SIZE = Math.floor((CANVAS_SIZE - GAP_SIZE * (CELLS_PER_SIDE + 1)) / CELLS_PER_SIDE);
const LARGE_CELL_SIZE = CELL_SIZE * 2 + GAP_SIZE;

// DOM  requests
const canvas = document.querySelector('canvas');
const body = document.querySelector('body');
const regenerateButton = document.querySelector('#regenerate');
const saveToSpotifyButton = document.querySelector('#save-to-spotify');

const ctx = canvas.getContext('2d');

async function main() {
    const images = await preloadImages(ALBUM_COVERS);
    body.classList.add('images-loaded');
    
    regenerateButton.addEventListener('click', () => drawGrid(images));
    saveToSpotifyButton.addEventListener('click', () => saveCoverToSpotify());

    initCanvas();

    drawGrid(images);
}

function initCanvas() {
    ctx.canvas.width = CANVAS_SIZE;
    ctx.canvas.height = CANVAS_SIZE;
    ctx.fillStyle = BACKGROUND_COLOR;
}

function clearCanvas() {
    drawRectangle(0, 0, CANVAS_SIZE, CANVAS_SIZE, BACKGROUND_COLOR);
}

function drawGrid(images) {
    ctx.save();
    
    clearCanvas();
    
    // Create random permutation each time!
    images = shuffle(images);

    centerRotateCanvas(-TILT_ANGLE);
    
    // Place small images first
    let imageIndex = 0;
    for (let row = -EXTRA_CELLS; row < CELLS_PER_SIDE + EXTRA_CELLS; row++) {
        for (let col = -EXTRA_CELLS; col < CELLS_PER_SIDE + EXTRA_CELLS; col++) {
            const xcursor = col * (GAP_SIZE + CELL_SIZE) + GAP_SIZE;
            const ycursor = row * (GAP_SIZE + CELL_SIZE) + GAP_SIZE;
            ctx.drawImage(images[imageIndex], xcursor, ycursor, CELL_SIZE, CELL_SIZE);

            imageIndex = (imageIndex + 1) % images.length;
        }
    }   

    // Paste large album covers, iteratively
    const largeImageLocations = [[1, 0], [3, 3]];
    largeImageLocations.forEach(([row, col]) => {
        const xcursor = col * (GAP_SIZE + CELL_SIZE) + GAP_SIZE;
        const ycursor = row * (GAP_SIZE + CELL_SIZE) + GAP_SIZE;
        ctx.drawImage(images[imageIndex], xcursor, ycursor, LARGE_CELL_SIZE, LARGE_CELL_SIZE);
        imageIndex = (imageIndex + 1) % images.length;
    });
    
    ctx.restore();
}

async function preloadImages(imageSources) {
    const promises = imageSources.map(source => new Promise(resolve => {
        const image = new Image();
        image.crossOrigin = "anonymous"; // Needed to prevent a tainted canvas
        image.src = source;
        image.onload = () => resolve(image);
    }));
    
    return Promise.all(promises);
}

function drawRectangle(x, y, width, height, color) {
    ctx.save();
    ctx.fillStyle = color;
    ctx.fillRect(x, y, width, height);
    ctx.restore();
}

function centerRotateCanvas(degrees) {
    // Translate center point to the origin
    ctx.translate(ctx.canvas.width / 2, ctx.canvas.height / 2);
    ctx.rotate((Math.PI / 180) * degrees);
    ctx.translate(-ctx.canvas.width / 2, -ctx.canvas.height / 2);
}

function pickLargeCellLocations(numRows, numCols, numLargeCells) {

}

// See https://stackoverflow.com/a/2450976
function shuffle(array) {
    let currentIndex = array.length,  randomIndex;

    // While there remain elements to shuffle...
    while (currentIndex != 0) {

        // Pick a remaining element...
        randomIndex = Math.floor(Math.random() * currentIndex);
        currentIndex--;

        // And swap it with the current element.
        [array[currentIndex], array[randomIndex]] = [
        array[randomIndex], array[currentIndex]];
    }

    return array;
}

async function saveCoverToSpotify() {
    saveToSpotifyButton.disabled = true;

    const PREFIX = 'data:image/jpeg;base64,';
    const dataURL = canvas.toDataURL('image/jpeg').slice(PREFIX.length);

    try {
        const response = await fetch(
            `https://api.spotify.com/v1/playlists/${PLAYLIST_ID}/images`,
            {
                method: 'PUT',
                headers: {
                    Authorization: `Bearer ${SPOTIFY_ACCESS_TOKEN}`,
                    'Content-Type': 'image/jpeg'
                },
                body: dataURL
            });

        if (!response.ok) {
            throw new Error(`Unable to save Spotify playlist (${response.status} error)`);
        } else {
            alert('Successfully set the cover image');
        }
    } catch (e) {
        alert(`Failed to upload image to Spotify: ${e}`)
    }
    
    saveToSpotifyButton.disabled = false;
}

main();