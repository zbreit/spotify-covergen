// Global settings object (updated by settings GUI)
let SETTINGS = {
    canvasSize: 640
};

// DOM  requests
const canvas = document.querySelector('canvas');
const body = document.querySelector('body');
const regenerateButton = document.querySelector('#regenerate');
const saveToSpotifyButton = document.querySelector('#save-to-spotify');
const ctx = canvas.getContext('2d');
let IMAGES = [];
let CURRENT_IMAGES = [];

async function main() {
    IMAGES = await preloadImages(ALBUM_COVERS);
    body.classList.add('images-loaded');
    
    regenerateButton.addEventListener('click', drawRandomGrid);
    saveToSpotifyButton.addEventListener('click', saveCoverToSpotify);

    SETTINGS = createOptimalGridSettings(IMAGES.length);
    setupSettingsGUI();

    initCanvas();
    drawRandomGrid();
}

function initCanvas() {
    ctx.canvas.width = SETTINGS.canvasSize;
    ctx.canvas.height = SETTINGS.canvasSize;
    ctx.fillStyle = SETTINGS.backgroundColor;
}

/**
 * Picks  the best grid settings for the given number of images
 */
function createOptimalGridSettings(imageCount) {
    const settings = {};
    const MAX_CELLS_PER_SIDE = 6;

    settings.backgroundColor = "#2C2C3C";
    settings.tiltAngle = 15;
    settings.canvasSize = 640;
    settings.gapSize = 8;
    settings.maxCellsPerSide = Math.min(MAX_CELLS_PER_SIDE, Math.floor(Math.sqrt(imageCount) - 1));
    settings.cellsPerSide = settings.maxCellsPerSide;
    settings.numLargeCells = Math.max(0, settings.cellsPerSide - 2);
    settings.largeImageLocations = pickLargeCellLocations(settings.cellsPerSide, settings.numLargeCells);

    return settings;
}

function clearCanvas() {
    drawRectangle(0, 0, SETTINGS.canvasSize, SETTINGS.canvasSize, SETTINGS.backgroundColor);
}

function drawRandomGrid() {
    CURRENT_IMAGES = shuffle(IMAGES);
    drawGrid(CURRENT_IMAGES, SETTINGS);
}

function redrawGrid() {
    drawGrid(CURRENT_IMAGES, SETTINGS);
}

function drawGrid(images, settings) {
    // Derived settings (not user-controllable)
    const CELL_SIZE = Math.floor((settings.canvasSize - settings.gapSize * (settings.cellsPerSide + 1)) / settings.cellsPerSide);
    const LARGE_CELL_SIZE = 2 * CELL_SIZE + settings.gapSize;
    const EXTRA_CELLS = settings.tiltAngle == 0 ? 0 : 1;


    clearCanvas();
    ctx.save();
    console.log(`Drawing grid with ${images.length} images`)

    centerRotateCanvas(-settings.tiltAngle);

    const occupiedCells = getLargeImageCells(settings.largeImageLocations);
    let imageIndex = 0;
    const drawNextImage = (row, col, size) => {
        const xcursor = col * (settings.gapSize + CELL_SIZE) + settings.gapSize;
        const ycursor = row * (settings.gapSize + CELL_SIZE) + settings.gapSize;
        ctx.drawImage(images[imageIndex], xcursor, ycursor, size, size);

        console.log('Drawing image', imageIndex);

        imageIndex = (imageIndex + 1) % images.length;
    };
    
    // Place small images first. Don't draw a small image underneath a big image
    // (otherwise, we may use up our images too fast)
    for (let row = -EXTRA_CELLS; row < settings.cellsPerSide + EXTRA_CELLS; row++) {
        for (let col = -EXTRA_CELLS; col < settings.cellsPerSide + EXTRA_CELLS; col++) {
            if (!occupiedCells.has(locationString(row, col))) {
                drawNextImage(row, col, CELL_SIZE);
            }
        }
    }   

    // Paste large album covers, iteratively
    settings.largeImageLocations.forEach(([row, col]) => {
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

/**
 * Given the location of the top-left corners of each large image, return a set
 * all cells that the large images occupy.
 */
function getLargeImageCells(largeImages) {
    const occupiedCells = new Set();

    largeImages.forEach(([row, col]) => {
        occupiedCells.add(locationString(row, col));
        occupiedCells.add(locationString(row + 1, col));
        occupiedCells.add(locationString(row, col + 1));
        occupiedCells.add(locationString(row + 1, col + 1));
    });

    return occupiedCells;
}

/**
 * Converts a grid coordinate into a representative string (row, col)
 */
function locationString(row, col) {
    return `${row},${col}`;
}

function range(size) {
    return [...Array(size).keys()];
}

function pickRandomSubarray(array, size) {
    const shuffled = shuffle(array);

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
function shuffle(originalArray) {
    const array = originalArray.slice(0);
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

function setupSettingsGUI() {
    const gui = new dat.GUI();

    gui.addColor(SETTINGS, 'backgroundColor').onChange(redrawGrid);
    gui.add(SETTINGS, 'tiltAngle', -180, 180, 5).onChange(redrawGrid);
    gui.add(SETTINGS, 'gapSize', 0, 32, 1).onChange(redrawGrid);
    gui.add(SETTINGS, 'cellsPerSide', 1, SETTINGS.maxCellsPerSide, 1).onChange(redrawGrid);
    gui.add(SETTINGS, 'numLargeCells', 0, SETTINGS.cellsPerSide - 1, 1).onFinishChange(() => {
        SETTINGS.largeImageLocations = pickLargeCellLocations(SETTINGS.cellsPerSide, SETTINGS.numLargeCells);
        redrawGrid();
    });
    // gui.add(SETTINGS, 'largeImageLocations').onChange(redrawGrid);
    console.log(gui.getSaveObject());
}

main();