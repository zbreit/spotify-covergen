// Settings
const BACKGROUND_COLOR = "#2f3030";
const TILT_ANGLE = 15;
const CANVAS_SIZE = 640;
const MAX_CELLS_PER_SIDE = 7;

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
    const CELLS_PER_SIDE = Math.min(MAX_CELLS_PER_SIDE, Math.floor(Math.sqrt(images.length)))
    const NUM_LARGE_CELLS = Math.max(0, CELLS_PER_SIDE - 2);
    const EXTRA_CELLS = TILT_ANGLE == 0 
        ? 0 
        : Math.max(1, Math.floor(CELLS_PER_SIDE / 3));
    const GAP_SIZE = 8;
    const CELL_SIZE = Math.floor((CANVAS_SIZE - GAP_SIZE * (CELLS_PER_SIDE + 1)) / CELLS_PER_SIDE);
    const LARGE_CELL_SIZE = CELL_SIZE * 2 + GAP_SIZE;

    clearCanvas();
    ctx.save();
    
    // Create random permutation each time!
    images = shuffle(images);
    console.log(`Drawing grid with ${images.length} images`)

    centerRotateCanvas(-TILT_ANGLE);

    let imageIndex = 0;
    const drawNextImage = (row, col, size) => {
        const xcursor = col * (GAP_SIZE + CELL_SIZE) + GAP_SIZE;
        const ycursor = row * (GAP_SIZE + CELL_SIZE) + GAP_SIZE;
        ctx.drawImage(images[imageIndex], xcursor, ycursor, size, size);
        imageIndex = (imageIndex + 1) % images.length;
    };
    
    // Place small images first
    for (let row = -EXTRA_CELLS; row < CELLS_PER_SIDE + EXTRA_CELLS; row++) {
        for (let col = -EXTRA_CELLS; col < CELLS_PER_SIDE + EXTRA_CELLS; col++) {
            drawNextImage(row, col, CELL_SIZE);
        }
    }   

    // Paste large album covers, iteratively
    const largeImageLocations = pickLargeCellLocations(CELLS_PER_SIDE, NUM_LARGE_CELLS);
    largeImageLocations.forEach(([row, col]) => {
        drawNextImage(row, col, LARGE_CELL_SIZE);
    });
    
    ctx.restore();
}

/**
 * Returns a list of locations where large cells can be placed in a
 * `sideLength` by `sideLength` grid.
 * 
 * The locations are chosen based on a heuristic
 */
function pickLargeCellLocations(cellsPerSide, count) {
    const locations = [];

    let rows = pickRandomSubarray(range(cellsPerSide - 1), count);
    rows.sort();

    // Choose a column based on the last row and col
    let lastLocation = [-100, -100];
    let lastLastLocation = [-100, -100];
    rows.forEach(row => {
        let possibleCols = range(cellsPerSide - 1);
        let illegalCols = [];

        if (row - lastLocation[0] === 1) {
            // Remove any columns that could overlap with the large cell
            // in the previous row. Such a collision can only occur if the
            // current and last row are one apart.
            illegalCols.push(
                (lastLocation[1] - 1) % (cellsPerSide - 1),
                lastLocation[1],
                (lastLocation[1] + 1) % (cellsPerSide - 1)
            );
        } 

        // Don't want any large cells that are 2 rows apart to be vertically-aligned
        if (row - lastLocation[0] === 2) {
            illegalCols.push(lastLocation[1]);
        }

        if (row - lastLastLocation[0] === 2) {
            illegalCols.push(lastLastLocation[1]);
        }
        
        // Subtract away any illegal columns
        possibleCols = possibleCols.filter(col => !(illegalCols.includes(col)));

        const col = pickRandomSubarray(possibleCols, 1)[0];
        const location = [row, col];
        locations.push(location);

        lastLastLocation = lastLocation;
        lastLocation = location;

        console.log(`Row ${row}: Chose ${col} from [${possibleCols}]`);
    });

    return locations;
}

function getEmptySquareMatrix(sideLength) {
    const grid = Array(sideLength);

    for (let i = 0; i < grid.length; i++) {
        grid[i] = Array(sideLength);
    }

    return grid;
}

function range(size) {
    return [...Array(size).keys()];
}

function pickRandomSubarray(array, size) {
    const shuffled = array.slice(0);
    shuffle(shuffled);

    return shuffled.slice(0, size);
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

// See https://stackoverflow.com/a/2450976
function shuffle(array) {
    let currentIndex = array.length,  randomIndex;

    // While there remain elements to shuffle...
    while (currentIndex != 0) {

        // Pick a remaining element...
        randomIndex = Math.floor(Math.random() * currentIndex);
        currentIndex--;

        // And swap it with the current element.
        [array[currentIndex], array[randomIndex]] = [array[randomIndex], array[currentIndex]];
    }

    return array;
}

async function saveCoverToSpotify() {
    saveToSpotifyButton.disabled = true;

    const PREFIX = 'data:image/jpeg;base64,';
    const QUALITY = 0.8;
    const dataURL = canvas.toDataURL('image/jpeg', QUALITY).slice(PREFIX.length);

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