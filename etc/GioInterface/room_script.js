let pathInterval = null, roomInterval;
let mainCanvas = null;
let gioMapURL = "http://localhost:5000/";
let wotServerURL = "http://131.114.73.148:2000/";
let newAreaButton = null, deleteAreaButton = null, reloadButton = null;
let pathButton = null;
let infoDiv = null;
let popupIndex = 0;

let circles = [];
let users = [];

/* --- FUNZIONI DI UTILITY --- */

function getRoomEnv(roomId,callback,bool = false){ //WoT
    roomId = roomId.replace("/","");
    let xml = new XMLHttpRequest();
    xml.onreadystatechange = function () {
        if (xml.readyState === 4) {
            if(xml.status === 200){
                var data = JSON.parse(xml.responseText);
                callback(data)
            }
        }
    };
    xml.open("GET", wotServerURL+'room'+roomId+"/all/properties", bool);
    xml.send(null);
}


function setRoomEnv(room_number,card){ //WoT

    getRoomEnv(room_number,function(data){

        if(data["lightL"] != undefined){card.querySelector('.env').innerHTML = "Light: "+data["lightL"].toLowerCase();}
        else{card.querySelector('.env').innerHTML = "light: n/a";}
        if(data["temperatureL"] != undefined){card.querySelector('.env').innerHTML += " - Temp: "+data["temperatureL"].toLowerCase().replace("_"," ");}
        else{card.querySelector('.env').innerHTML += " - temp: n/a";}

    },true);

}

// effettua una richiesta HTTP
function doRequest(command, method, args, callback, err_callback) {
    let xml = new XMLHttpRequest();
    xml.onreadystatechange = function () {
        if (xml.readyState === 4) {
            if(xml.status === 200)
                callback(xml.responseText);
            else
                if(err_callback !== null)
                    err_callback(xml.responseText);
                else
                    changeInfoText(JSON.parse(xml.responseText).message);
        }
    };
    xml.open(command, gioMapURL + method, true);
    if(args != null)
    {
        xml.setRequestHeader('Content-type','application/json');
    }

    xml.send(args);
}

/* richiede il calcolo del cammino minimo tra 'begin' e 'end' (entrambe stanze)
   impostando i parametri del path temporaneo dell'oggetto Canvas
 */
function minPath(begin, end) {
    let req = 'paths?id_begin=' + begin.id +
        '&id_end=' + end.id + '&min_path=1';
    doRequest('GET', req, null, function (response)
    {
        response = JSON.parse(response);
        let nodes = response.nodes;
        let path = mainCanvas.tempPath;
        if(response.id_end === path.begin.id) //path salvato al contrario
            nodes = nodes.reverse();

        path.end = end;
        path.nodes = nodes;
        mainCanvas.pathing = 'showPath';
        mainCanvas.valid = false;
        mainCanvas.draw();
    });
}

// carica una shape sul DB, aggiungendola o aggiornandola
function uploadShape(shape, isNew) {
    let command = isNew ? 'POST' : 'PUT';
    let req = isNew ? 'rooms' : ('rooms/' + shape.id);
    doRequest(command, req, JSON.stringify(shape),function (response)
    {
            response = JSON.parse(response);
            changeInfoText(response.message);
            if(command === 'POST')
                mainCanvas.shapes[mainCanvas.shapes.indexOf(shape)].id = response.id_room;
    });
}

// carica una nuovo path sul DB, aggiugnendolo o aggiornandolo
function uploadPath(path, isNew) {
    let command = isNew ? 'POST' : 'PUT';
    let req = isNew ? 'paths' : ('paths/' + path.id);
    doRequest(command, req, path.toJSON(), function (response)
    {
        response = JSON.parse(response);
        changeInfoText(response.message);
    });
}

//dati due numeri, li ritorna come coppia
function point(x, y) {
    return { x: x, y: y};
}

// dati due punti, ritorna l'angolo tra essi in gradi
function calculateAngle(p1, p2) {
    let angle = 0;
    if (p2.x === p1.x)
    {
        if(p2.y < p1.y) angle = 0;
        else angle = Math.PI;
    }
    else if(p2.y === p1.y)
    {
        if(p2.x < p1.x) angle = - Math.PI / 2;
        else angle = Math.PI / 2;
    }
    else
    {
        //coefficiente angolare della retta passante per p1 e p2
        angle = Math.atan2(p2.y - p1.y, p2.x - p1.x);
        angle += Math.PI / 2;
    }
    return angle;
}

/*
 dati due punti, ritorna se essi sono adiacenti,
 ovvero se hanno stessa 'x' o stessa 'y'
 */
function isAdjacent(p1, p2, len)
{
    if(len === 1)
        return true;
    return ((p1.x === p2.x) && (Math.abs(p1.y - p2.y) < 200)) ||
        ((p1.y === p2.y) && (Math.abs(p1.x - p2.x) < 200))
}

// date le coordinate di un cerchio, controlla se un punto è al suo interno
function onCircle(ctx, x, y, radius, px, py)
{
    ctx.beginPath();
    ctx.arc(x, y, radius, 0, 2 * Math.PI);
    ctx.closePath();
    return ctx.isPointInPath(px,py);
}

// ritorna 'strDate' nel formato 'dd/MM/yyyy'
function getFormattedDate(strDate) {
    let parts = strDate.split('-');
    return parts[2] + "/" + parts[1] + "/" + parts[0];
}

// imposta i parametri del popup da mostrare cliccando su una stanza
function setPopup(clickPos, users, room_number, room_name)
{
    let popup = document.getElementById("popup");
    let content = document.getElementById('card-template');
    while(popup.firstChild)
        popup.removeChild(popup.firstChild);

    let name = "STANZA " + room_number;
    if(room_name) name += " - " + room_name;

    if (users !== null && users !== undefined && users.length !== 0)
    {
        users.forEach(function(user) {
            let card = content.querySelector('.card').cloneNode(true);
            card.querySelector('.cardName').innerHTML = name;
            //card.querySelector('.userImg').src = user.img_url;
            card.querySelector('.userName').innerHTML = user.name + " " + user.surname;
            card.querySelector('.userTitle').innerHTML = user.title;
            card.querySelector('.userPhone').innerHTML += " " + user.phone_number;
            let start_date = getFormattedDate(user.start_contract);
            let end_date = getFormattedDate(user.end_contract);
            card.querySelector('.userContract').innerHTML += start_date + " - " + end_date;
            card.querySelector('.userMail').href = "mailto:"+user.email;
            card.querySelector('.userSite').href = user.website;

            setRoomEnv(room_number,card);

            popup.appendChild(card);
        });
    }
    else
    {
        let content = document.getElementById('empty-template');
        let card = content.querySelector('.card').cloneNode(true);
        card.querySelector('.cardName').innerHTML = name;

        setRoomEnv(room_number,card);

        popup.appendChild(card);
    }

    popup.style.display = "block";
    popup.style.position =  'absolute';

    let popupWidth = popup.firstElementChild.clientWidth;
    let canvasDiv = document.getElementById('canvas-wrap');
    if(clickPos.x + popupWidth > canvasDiv.clientWidth)
        clickPos.x -= popupWidth;

    popup.style.left = (clickPos.x + 5) + 'px';
    let popupHeight = popup.firstElementChild.clientHeight;
    if(clickPos.y + popupHeight > document.documentElement.clientHeight)
        clickPos.y -= popupHeight;



    popup.style.top = clickPos.y + 'px';
    popup.style.display = "none";
}

// cambia la card da mostrare all'interno del popup
function changeCard(n) {
    showCard(popupIndex += n);
}

// mostra una delle card all'interno del popup, nascondendo le altre
function showCard(n) {
    let i;
    let popup = document.getElementById("popup");
    let cards = popup.getElementsByClassName('card');
    if(cards.length > 0)
    {
        if(n > cards.length-1) popupIndex = 0;
        if(n < 0) popupIndex = cards.length-1;

        for(i = 0; i < cards.length; i++)
        {
            cards[i].style.display = "none";
        }

        let shownCard = cards[popupIndex];
        shownCard.style.display = "block";

        // mostro solo le arrows necessarie
        if(cards[0] === shownCard)
            if(shownCard.querySelector('.arrowLeft'))
                shownCard.querySelector('.arrowLeft').style.display = "none";

        if(cards[cards.length-1] === shownCard)
            if(shownCard.querySelector('.arrowRight'))
                shownCard.querySelector('.arrowRight').style.display = "none";
    }

    //se è già visibile, lo nascondo e poi lo mostro nella corretta posizione
    popup.style.display = "block";
}

// nasconde il popup visibile al click su di una stanza
function hidePopup() {
    document.getElementById("popup").style.display = "none";
    popupIndex = 0;
}

// rimuove il pin di un path precedentemente disegnato
function hidePin() {
    let img = document.getElementById('pinImage');
    if(img !== null)
    {
        let visibility = window.getComputedStyle(img).visibility;
        if(visibility !== 'hidden')
        {
            let ctx = mainCanvas.ctx;
            ctx.drawImage(img, img.style.left, img.style.top);
            document.body.removeChild(img);
            mainCanvas.valid = false;
            mainCanvas.draw();
        }
    }
}

// ritorna il centro di una stanza
function center(shape) {
    return {x: shape.x + (shape.width/2), y: shape.y + (shape.height/2)};
}

// ritorna la distanza euclidea tra i punti 'p1' e 'p2'
function dist(p1, p2) {
    return Math.sqrt((p2.x - p1.x) * (p2.x - p1.x) + (p2.y - p1.y) * (p2.y - p1.y));
}

/* --- OGGETTI --- */

/**
 * Rappresenta un percorso fra due stanze
 * @param id identificativo univoco del path
 * @param begin stanza di partenza
 * @param end stanza di arrivo
 * @param color colore del path quando viene disegnato
 * @param nodes punti che formano il path
 */
function Path(id, begin, end, color)
{
    this.id = id || null;
    this.begin = begin;
    this.end = end || null;
    this.color = color || 'rgb(0,143,0)';
    this.nodes = [];

    // disegna un path come una linea spezzata
    Path.prototype.draw = function (ctx) {
        let firstPoint = true;

        ctx.strokeStyle = this.color;
        ctx.lineWidth = 5;
        ctx.beginPath();

        this.nodes.forEach(p => {
            if(firstPoint)
            {
                ctx.moveTo(p.x, p.y);
                firstPoint = false;
            }
            else
                ctx.lineTo(p.x, p.y);
        });

        ctx.stroke();
    };

    // disegna il path come un' animazione di passi, stile "Mappa del malandrino" di HP
    Path.prototype.animate = function (ctx) {

        if(pathInterval !== null)
            clearInterval(pathInterval);

        if(roomInterval !== null)
            clearInterval(roomInterval);

        mainCanvas.unselectItem();
        let curr = 0;

        let nodes = this.nodes;
        //aggiungo coordinate del centro dell'inizio e della fine del percorso
        nodes.unshift(this.begin.center);
        nodes.push(this.end.center);
        let length = this.nodes.length;
        let angle = 0;
        let dx = new Image();
        dx.src = "img/dx.png";
        let sx = new Image();
        sx.src = "img/sx.png";
        let pin = new Image();
        pin.src = "img/pin.png";
        let foot = false; // FALSE -> dx, TRUE -> sx
        let animate_nodes = this.nodes;
        let dv = document.getElementById("canvas-wrap");


        disableButton(true);
        changeInfoText("");
        pathInterval = setInterval(function ()
        {
            let node = animate_nodes[curr];
            let midNode = animate_nodes[curr+1];
            let left = dv.scrollLeft;
            let right = dv.clientWidth + left;

            //first node
            if(curr === 0 && (node.x < left || node.x > right ))
                dv.scrollTo(node.x - 100, 0);

            if(node.x < left + 100) dv.scrollBy(-200, 0);
            else if (node.x > right - 100) dv.scrollBy(200, 0);

            angle = calculateAngle(node, midNode);
            ctx.translate(node.x, node.y);
            ctx.rotate(angle);
            if(foot)
                ctx.drawImage(sx, -sx.width/2, -sx.height/2);
            else
                ctx.drawImage(dx, -dx.width/2, -dx.height/2);

            ctx.rotate(-angle);
            ctx.translate(-node.x, -node.y);
            foot = !foot;
            curr++;
            let distance = dist(node, midNode);
            // se due punti sono troppo distanti ne aggiungo un altro nel mezzo
            if (distance > 50 && curr !== length-1)
            {
                let toAdd = Math.floor(distance/50) +1;
                let p = curr;
                for(let i = 1; i < toAdd; i++)
                {
                    // divide la retta in 'toAdd' parti uguali
                    let m = {x: node.x + (i/toAdd)*(midNode.x - node.x) , y: node.y + (i/toAdd)*(midNode.y - node.y)};
                    animate_nodes.splice(p,0,m);
                    p++;
                    length++;
                }
            }

            if(curr === length-1)
            {
                node = nodes[curr];
                ctx.translate(node.x, node.y);
                ctx.drawImage(pin, -pin.width/2, -pin.height/2);
                ctx.translate(-node.x, -node.y);
                clearInterval(pathInterval);
                mainCanvas.pathing = false;
                mainCanvas.tempPath = null;
                pathButton.innerText = "Start Path";
                disableButton(false);
            }
        },300);

    };

    //aggiunge un punto al percorso
    Path.prototype.addPoint = function (p) {
        this.nodes.push(p);
    };

    // ritorna la rappresentazione JSON del percorso
    Path.prototype.toJSON = function () {
        let app = [];
        this.nodes.shift(); // eliminio punto di partenza
        this.nodes.pop(); // elimino punto di arrivo
        this.nodes.forEach(p => {
            app.push(p.id_node);
        });
      return JSON.stringify(
          {
              id_path: this.id,
              id_begin: this.begin.id,
              id_end: this.end.id,
              nodes: app
          });
    };
}

/**
 * Rappresenta una stanza (area del canvas rettangolare)
 * @param id identificativo univoco dell'area
 * @param [x,y] coordinate del punto in alto a sx dell'area al momento della creazione
 * @param [width,height] larghezza e altezza dell'area
 * @param color colore dell'area (bordo e riempimento)
 * @param [number,name,type] servono a identificare il nome della stanza
 */
function Room(id, x, y, width, height, color)
{
    this.id = id || null;
    this.name = null;
    this.number = null;
    this.type = null;
    this.x = x || 0;
    this.y = y || 0;
    this.width = width || 1;
    this.height = height || 1;
    this.color = color || 'rgba(0,0,0,1)';
    this.center = center(this);

    // disegna la stanza (senza riempimento)
    Room.prototype.draw = function (ctx) {
        ctx.strokeStyle = this.color;
        ctx.lineWidth = 1;
        ctx.strokeRect(this.x, this.y, this.width, this.height);
    };

    // disegna un cerchio al centro della stanza
    Room.prototype.drawCenter = function (ctx, selected) {

        ctx.beginPath();
        ctx.arc(this.center.x, this.center.y, 8, 0, 2 * Math.PI);
        ctx.fillStyle = (selected) ? 'rgb(0,143,10)' : 'rgb(143,0,10)';
        ctx.fill();
    };

    // pick correlation con la stanza; controlla che un punto sia al suo interno
    Room.prototype.contains = function(ctx, mx, my) {
        ctx.beginPath();
        ctx.rect(this.x, this.y, this.width, this.height);
        ctx.closePath();
        return ctx.isPointInPath(mx,my)
    };

    // pick correlation con il centro della stanza; controlla che un punto sia al suo interno
    Room.prototype.onCenter = function (ctx, mx, my) {
        return onCircle(ctx,this.center.x, this.center.y, 8, mx, my);
    };

    // disegna la stanza (con riempimento e una certa opacità)
    Room.prototype.fill = function (ctx, opacity, color) {
 
        ctx.clearRect(this.x, this.y, this.width, this.height);
        let fillColor = color;
        if(opacity)
        {
            let begin_idx = fillColor.lastIndexOf(',')+1;
            fillColor = fillColor.substring(0,begin_idx) + opacity + ')';
        }
        ctx.fillStyle = fillColor;
        ctx.fillRect(this.x, this.y, this.width, this.height);
    }

        // disegna la stanza (senza riempimento)
    Room.prototype.drawAndFill = function (ctx) {
        ctx.clearRect(this.x, this.y, this.width, this.height);
        let fillColor = this.color;
        ctx.fillStyle = fillColor;
        ctx.fillRect(this.x, this.y, this.width, this.height);
    };

            // disegna la stanza (senza riempimento)
    Room.prototype.drawBorder = function (ctx) {
        thickness = 1;
        ctx.fillStyle='#000';
        ctx.fillRect(this.x - (thickness), this.y - (thickness), this.width + (thickness * 2), this.height + (thickness * 2));
    };

}

/**
 * Oggetto principale della pagina, il canvas contenente l'immagine del dipartimento
 * su cui vengono svolte le principali operazioni
 */
function GioCanvas(canvas)
{
    this.canvas = canvas;
    this.ctx = canvas.getContext('2d');
    this.canvas.globalCompositeOperation = 'destination-atop';
    this.width = canvas.width;
    this.height = canvas.height;
    this.handlesSize = 8;

    /* variabili per tenere traccia dello stato del canvas */

    this.valid = false;  // se valid = false, il canvas ridisegna il suo contenuto
    this.shapes = [];  // insieme di aree all'interno del canvas
    this.selectedItem = null;  // stanza attualmente selezionata all'interno del canvas

    this.tempArea = null; // stanza temporaneamente in fase di editing
    this.tempPath = null; // percorso temporaneamente in fase di di editing / visualizzazione
    this.lastPopup = null; // ultimo popup visualizzato

    this.isNew = false; // indica se 'tempArea' è nuova o è un'area già presente in fase di editing

    /* variabili di stato delle principali operazioni */

    this.dragging = false; // trascinamento di un'area
    this.drawing = false; // disegno di una nuova area
    this.deleting = false; // eliminazione di una nuova area
    this.pathing = false; // creazione / visualizzazione di un percorso
    this.currentHandle = false; // ridimensionamento di un'area


    this.oldPos = {x: 0, y: 0};
    // variabili per tenere traccia dello spostamento in fase di dragging
    this.dragoffX = 0;
    this.dragoffY = 0;

    // variabili per conoscere la posizione del canvas all'interno della pagina
    this.canvas_space = this.canvas.getBoundingClientRect();
    this.canvasOffset = {x: this.canvas_space.left, y: this. canvas_space.top};

    // chiusura necessaria per avere un riferimento al canvas nella gestione degli eventi
    let gioState = this;

    /* opzioni del canvas */

    this.selectionWidth = 3;
    this.backgroundImage = null;
    this.fps = 60;
    setInterval(function () { gioState.draw(); }, gioState.fps);

    /* EVENT LISTENERS */
    canvas.addEventListener('selectstart', function (e) {e.preventDefault();return false;}, false);

    canvas.addEventListener('mousedown', function (e) {
        if(e.which !== 1) // solo click sinistro
            return;

        if(gioState.pathing && gioState.pathing === "showPath")
            return;

        hidePopup();
        hidePin();

        if(roomInterval !== null)
            clearInterval(roomInterval);

        let mouse = gioState.getMouse(e);

        gioState.dragoffX = mouse.x;
        gioState.dragoffY = mouse.y;

        if(gioState.currentHandle)
        {
            gioState.dragging = true;
            gioState.valid = false;
            return;
        }

        if(gioState.tempArea != null && gioState.tempArea.contains(gioState.ctx, mouse.x, mouse.y))
        {
            gioState.selectItem(gioState.tempArea, mouse);
            return;
        }

        if(!gioState.drawing) // non sto disegnando
        {
            let shapes = gioState.shapes;
            let len = shapes.length;
            let ctx = gioState.ctx;

            for(let i = len-1; i>=0; i--)
            {
                //click su una shape mentre non sto editando
                if(shapes[i].contains(ctx, mouse.x,mouse.y) && gioState.tempArea === null)
                {
                    gioState.selectItem(shapes[i], mouse);

                    if(gioState.deleting)
                    {
                        if(confirm('Sicuro di voler eliminare la stanza ' + shapes[i].name + '?'))
                        {
                            doRequest('DELETE', 'rooms/' + shapes[i].id, null, function (response) {
                                let a = JSON.parse(response);
                                changeInfoText(a.message);
                                gioState.unselectItem();
                            });


                            // elimino visivamente la stanza
                            gioState.shapes.splice(gioState.shapes.indexOf(shapes[i]), 1);
                        }
                        gioState.deleting = false;
                        disableButton(false);
                    }
                    else
                    {
                        if(gioState.pathing)
                        {
                            switch (gioState.pathing)
                            {
                                case "selectBegin":
                                {
                                    if(shapes[i].onCenter(ctx, mouse.x, mouse.y))
                                    {
                                        gioState.tempPath = new Path();
                                        gioState.tempPath.begin = shapes[i];
                                        gioState.pathing = 'selectEnd';
                                        changeInfoText('Seleziona la stanza a cui arrivare');
                                    }
                                    gioState.dragging = true;
                                    break;
                                }

                                case "selectEnd":
                                {
                                    if(shapes[i].onCenter(ctx, mouse.x, mouse.y))
                                    {
                                        if(shapes[i] === gioState.tempPath.begin)
                                            changeInfoText('Scegli una stanza diversa da quella di partenza!');
                                        else
                                        {
                                            // controllo che il path non esista già
                                            let req = 'paths?id_begin=' + gioState.tempPath.begin.id +
                                                      '&id_end=' + shapes[i].id;
                                            doRequest('GET', req, null, function (response)
                                            {
                                                response = JSON.parse(response);
                                                if(confirm('Esiste gia\' un percorso tra le due stanze, vuoi sovrascriverlo? \n' +
                                                    'Se annulli ti verra\' mostrato il path corrente.'))
                                                {
                                                    gioState.isNew = false;
                                                    gioState.tempPath.end = shapes[i];
                                                    gioState.pathing = "beginPath";
                                                    gioState.dragging = true;
                                                    gioState.tempPath.id = response.id_path;
                                                }
                                                else
                                                {
                                                    let nodes = response.nodes;
                                                    if(response.id_end === gioState.tempPath.begin.id) //path salvato al contrario
                                                        nodes = nodes.reverse();

                                                    gioState.tempPath.end = shapes[i];
                                                    gioState.tempPath.nodes = nodes;
                                                    gioState.pathing = 'showPath';
                                                }

                                                gioState.valid = false;
                                                gioState.draw();

                                            },
                                                // non esiste il path, lo sto creando
                                                function (response) {
                                                    if(confirm("Vuoi calcolare il path minimo? " +
                                                        "Se annulli potrai disegnare e salvare un path personalizzato"))
                                                    {
                                                        /*let req = 'paths?id_begin=' + gioState.tempPath.begin.id +
                                                            '&id_end=' + shapes[i].id + '&min_path=1';
                                                        doRequest('GET', req, null, function (response)
                                                        {
                                                            response = JSON.parse(response);
                                                            let nodes = response.nodes;
                                                            if(response.id_end === gioState.tempPath.begin.id) //path salvato al contrario
                                                                nodes = nodes.reverse();

                                                            gioState.tempPath.end = shapes[i];
                                                            gioState.tempPath.nodes = nodes;
                                                            gioState.pathing = 'showPath';
                                                            gioState.valid = false;
                                                            gioState.draw();
                                                        });*/
                                                        minPath(gioState.tempPath.begin, shapes[i]);
                                                    }
                                                    else
                                                    {
                                                        gioState.isNew = true;
                                                        gioState.tempPath.end = shapes[i];
                                                        changeInfoText('Disegna il percorso, fino a raggiungere la stanza di arrivo');
                                                        gioState.pathing = 'beginPath';
                                                        gioState.dragging = true;
                                                    }
                                                    gioState.valid = false;
                                                    gioState.draw();
                                                });
                                        }
                                    }
                                    break;
                                }

                                case 'beginPath':
                                {
                                    if(shapes[i].onCenter(ctx, mouse.x, mouse.y))
                                    {
                                        //array dei punti vuoto
                                        if(gioState.tempPath.nodes.length === 0)
                                        {
                                            //devo iniziare per forza dal punto di partenza
                                            if(shapes[i] !== gioState.tempPath.begin)
                                                changeInfoText('Inizia a disegnare il percorso dal punto di partenza!');
                                            else
                                            {
                                                gioState.tempPath.addPoint(center(shapes[i]));
                                                gioState.pathing = "drawPath";
                                            }
                                        }
                                    }
                                    gioState.draw();
                                    break;
                                }
                            }
                        }
                        else // mostro il popup
                        {
                            let shape = shapes[i];
                            if(shape.contains(gioState.ctx, mouse.x, mouse.y))
                            {
                                if(shape !== gioState.lastPopup)
                                {
                                    let pos = {x: e.pageX, y: e.pageY};
                                    let cards = users.filter(function (el) {return el.office === shape.id});
                                    setPopup(pos, cards, shape.number, shape.name);
                                }
                                showCard(popupIndex);
                                gioState.lastPopup = shape;
                            }
                        }
                    }

                    // ridisegno per mostrare le modifiche effettuate
                    gioState.valid = false;
                    gioState.draw();
                    return;
                }
            }
            /* se arrivo qui non ho selezionato nulla
            in caso ci sia qualcosa di selezionato, lo deseleziono */
            gioState.unselectItem();
        }
        else // sto disegnando una nuova area
        {
            if(gioState.tempArea === null)
            {
                gioState.tempArea = new Room();
                gioState.tempArea.name = document.getElementById('area_name').value;
                gioState.tempArea.type = document.getElementById('area_type').value;
                gioState.tempArea.color = document.getElementById('area_color').value;
            }
            gioState.tempArea.x = mouse.x;
            gioState.tempArea.y = mouse.y;
        }

        gioState.dragging = true;

    }, true);


    canvas.addEventListener('mousemove', function (e) {
        let mouse = gioState.getMouse(e);
        let previousHandle = gioState.currentHandle;
        if(gioState.pathing && gioState.pathing === "showPath")
            return;
        if(gioState.dragging)
        {
            hidePopup();

            if(gioState.pathing)
            {
                switch (gioState.pathing)
                {
                    case "beginPath":
                        break;
                    case "drawPath":
                    {
                        //sono arrivato all'area di arrivo
                        if(gioState.tempPath.end.contains(gioState.ctx, mouse.x, mouse.y))
                        {
                            gioState.tempPath.addPoint(gioState.tempPath.end.center);
                            gioState.pathing = 'confirm';
                            changeInfoText("Ecco fatto, hai raggiunto la stanza <b>" + gioState.tempPath.end.number + "</b>.<br>" +
                                "Conferma il percorso o premi ESC per annullare");
                        }
                        else
                        {
                            //controllo se sono su uno dei nodi del grafo
                            circles.forEach(function (c)
                            {
                                let len = gioState.tempPath.nodes.length;
                                if(onCircle(gioState.ctx,c.x,c.y,7,mouse.x, mouse.y))
                                {
                                    if(gioState.tempPath.nodes.includes(c))
                                    {
                                        // se ripasso su un nodo già presente, ridimensiono il path
                                        gioState.tempPath.nodes = gioState.tempPath.nodes.slice(0,gioState.tempPath.nodes.indexOf(c,1)+1)
                                    }
                                    else if(isAdjacent(c,gioState.tempPath.nodes[len-1],len))
                                        gioState.tempPath.addPoint(c);
                                }
                            });
                        }
                        break;
                    }
                }
                gioState.valid = false;
                gioState.draw();
                return;
            }

            if(gioState.currentHandle)
            {
                gioState.unselectItem();
                let tempArea = gioState.tempArea;
                switch (gioState.currentHandle)
                {
                    case 'topleft':
                        tempArea.width += tempArea.x - mouse.x;
                        tempArea.height += tempArea.y - mouse.y;
                        tempArea.x = mouse.x;
                        tempArea.y = mouse.y;
                        break;
                    case 'topright':
                        tempArea.width = mouse.x - tempArea.x;
                        tempArea.height += tempArea.y - mouse.y;
                        tempArea.y = mouse.y;
                        break;
                    case 'bottomleft':
                        tempArea.width += tempArea.x - mouse.x;
                        tempArea.x = mouse.x;
                        tempArea.height = mouse.y - tempArea.y;
                        break;
                    case 'bottomright':
                        tempArea.width = mouse.x - tempArea.x;
                        tempArea.height = mouse.y - tempArea.y;
                        break;

                    case 'top':
                        tempArea.height += tempArea.y - mouse.y;
                        tempArea.y = mouse.y;
                        break;

                    case 'left':
                        tempArea.width += tempArea.x - mouse.x;
                        tempArea.x = mouse.x;
                        break;

                    case 'bottom':
                        tempArea.height = mouse.y - tempArea.y;
                        break;

                    case 'right':
                        tempArea.width = mouse.x - tempArea.x;
                        break;
                }
            }
            else
            {
                if(gioState.drawing)
                {
                    gioState.tempArea.width = mouse.x - gioState.tempArea.x;
                    gioState.tempArea.height = mouse.y - gioState.tempArea.y;
                    gioState.valid = false;
                    gioState.draw();
                }
                else
                {
                    if(gioState.selectedItem)
                    {
                        // sposto l'oggetto non dal suo top-left, ma dal punto in cui ho clickato.
                        gioState.selectedItem.x = mouse.x - gioState.dragoffX;
                        gioState.selectedItem.y = mouse.y - gioState.dragoffY;
                        gioState.valid = false;
                        gioState.draw();
                    }

                    /*if(gioState.tempArea === null) // non sto facendo editing di una shape
                    {
                        gioState.translatePos.x = mouse.x - gioState.dragoffX;
                        gioState.translatePos.y = mouse.y - gioState.dragoffY;
                        gioState.valid = false;
                        gioState.draw();
                    }*/
                }
            }
        }
        else
            gioState.currentHandle = gioState.getHandle(mouse);

        if(gioState.dragging || gioState.currentHandle !== previousHandle)
        {
            gioState.valid = false;
            gioState.draw();
        }
    }, true);


    canvas.addEventListener('mouseup', function () {
        gioState.dragging = false;
        gioState.drawing = false;

    }, true);

    canvas.addEventListener('mouseleave', function () {
        gioState.dragging = false;
        gioState.drawing = false;
    }, true);


    canvas.addEventListener('mousewheel', function () {
        hidePopup();
    });


    canvas.addEventListener('dblclick', function (e) {
        if(gioState.pathing)
            return;
        let mouse = gioState.getMouse(e);

        //mouse = gioState.viewToWorld(mouse.x, mouse.y);

        hidePopup();

        // doppio click sull'area che sto disegnando --> la conferma
        if(gioState.tempArea !== null && gioState.tempArea.contains(gioState.ctx, mouse.x, mouse.y))
        {
            gioState.validateShape();
            gioState.drawing = false;
            return;
        }

        // doppio click su una delle aree già presenti --> ne permette il resize
        let shapes = gioState.shapes;
        let len = shapes.length;

        for(let i = len-1; i>=0; i--)
        {
            if(shapes[i].contains(gioState.ctx, mouse.x,mouse.y))
            {
                if(gioState.tempArea !== null)
                    gioState.validateShape();

                newAreaButton.disabled = true;
                deleteAreaButton.disabled = true;

                gioState.isNew = false;
                gioState.tempArea = shapes[i];
                // salvo lo stato corrente della shape in caso di annullamento dell'operazione
                gioState.oldPos = {x: shapes[i].x, y:shapes[i].y};
                gioState.shapes.splice(gioState.shapes.indexOf(shapes[i]), 1);

                /* apro il form per permettere la modifica dei parametri di una stanza */
                openForm(gioState.tempArea.number, gioState.tempArea.name, gioState.tempArea.type, gioState.tempArea.color);

                gioState.valid = false;
                gioState.draw();
                return;
            }
        }
    });


    /* FUNZIONI DEL CANVAS */

    /*GioCanvas.prototype.viewToWorld = function (x, y) {
        let newX = Math.abs(x - gioState.translatePos.x);
        let newY = Math.abs(y - gioState.translatePos.y);
        return {x: newX, y: newY};
    };*/

    GioCanvas.prototype.unselectItem = function () {
        if(this.selectedItem)
        {
            this.selectedItem = null;
            this.valid = false; // per pulire la vecchia selezione
        }
    };

    GioCanvas.prototype.selectItem = function (selection, mouse) {
        gioState.dragoffX = mouse.x - selection.x;
        gioState.dragoffY = mouse.y - selection.y;

        if(gioState.tempArea !== null) // sto editando una stanza
            gioState.dragging = true;
        gioState.selectedItem = selection;
        gioState.valid = false;
    };

    GioCanvas.prototype.clearCanvas = function () {
        this.ctx.clearRect(0,0,this.width, this.height);
        this.valid = false;
    };

    GioCanvas.prototype.addShape = function (shape) {
        this.shapes.push(shape);
        this.valid = false;
    };

    GioCanvas.prototype.validateShape = function () {
        gioState.tempArea.number = document.getElementById('area_number').value;
        gioState.tempArea.name = document.getElementById('area_name').value;
        gioState.tempArea.type = document.getElementById('area_type').value;
        gioState.tempArea.color = document.getElementById('area_color').value;
        gioState.tempArea.center = center(gioState.tempArea);
        gioState.shapes.push(gioState.tempArea);
        uploadShape(gioState.tempArea,gioState.isNew);
        gioState.tempArea = null;
        closeForm();
        gioState.valid = false;
        gioState.draw();
    };

    GioCanvas.prototype.validatePath = function () {
        uploadPath(gioState.tempPath, gioState.isNew);
        gioState.pathing = false;
        gioState.tempPath = null;
        gioState.valid = false;
        gioState.draw();
        disableButton(false);

    };


    GioCanvas.prototype.getMouse = function (e) {
        // div che contiene il canvas, può scrollare, e devo tener conto di tale spostamento nelle coordinate del mouse
        let div = document.getElementById('canvas-wrap');

        let mx = e.pageX - gioState.canvasOffset.x + div.scrollLeft;
        let my = e.pageY - gioState.canvasOffset.y + div.scrollTop;
        return point(mx, my);
    };

    GioCanvas.prototype.getHandle = function (mouse) {
        if(gioState.tempArea != null)
        {
            let tempArea = gioState.tempArea;
            let handlesSize = gioState.handlesSize;

            if (dist(mouse, point(tempArea.x, tempArea.y)) <= handlesSize) return 'topleft';
            if (dist(mouse, point(tempArea.x + tempArea.width, tempArea.y)) <= handlesSize) return 'topright';
            if (dist(mouse, point(tempArea.x, tempArea.y + tempArea.height)) <= handlesSize) return 'bottomleft';
            if (dist(mouse, point(tempArea.x + tempArea.width, tempArea.y + tempArea.height)) <= handlesSize) return 'bottomright';
            if (dist(mouse, point(tempArea.x + tempArea.width / 2, tempArea.y)) <= handlesSize) return 'top';
            if (dist(mouse, point(tempArea.x, tempArea.y + tempArea.height / 2)) <= handlesSize) return 'left';
            if (dist(mouse, point(tempArea.x + tempArea.width / 2, tempArea.y + tempArea.height)) <= handlesSize) return 'bottom';
            if (dist(mouse, point(tempArea.x + tempArea.width, tempArea.y + tempArea.height / 2)) <= handlesSize) return 'right';
        }
        return false;
    };

    GioCanvas.prototype.draw = function () {
        if(!gioState.valid)
        {
            let ctx = gioState.ctx;
            let shapes = gioState.shapes;
            this.clearCanvas();

            ctx.save();

            /* disegno il background */
            if(gioState.backgroundImage != null)
                ctx.drawImage(gioState.backgroundImage, 0,0);

            // ridisegno tutte le shapes
            let len = shapes.length;
            for(let i=0; i<len; i++)
            {
                let shape = shapes[i];
                if(shape.x > gioState.width || shapes.y > gioState.height ||
                    shape.x + shape.width < 0 || shape.y + shape.height < 0) continue;

                if(gioState.drawing || gioState.deleting || gioState.tempArea !== null)
                {
                    shape.draw(ctx);
                }

                //codice per disegnare pallini inizio e fine path
                if(gioState.pathing)
                {
                    if(gioState.tempPath !== null)
                    {
                        if ( (gioState.tempPath.begin === shape || gioState.tempPath.end === shape) && gioState.pathing !== 'showPath')
                            shape.drawCenter(ctx, true);
                        else
                        if(gioState.pathing !== "showPath")
                            shape.drawCenter(ctx, false);
                    }
                    else
                    if(gioState.pathing !== "showPath")
                        shape.drawCenter(ctx, false);

                }
            }

            if(gioState.pathing)
            {
                if(gioState.pathing !== "showPath")
                {
                    // disegno nodi del grafo del dipartimento
                    circles.forEach(function (c) {
                        ctx.beginPath();
                        ctx.arc(c.x, c.y, 7, 0, 2 * Math.PI);
                        if(gioState.tempPath != null && gioState.tempPath.nodes.includes(c))
                            ctx.fillStyle = 'rgb(0,143,10)';
                        else
                            ctx.fillStyle = 'rgb(0,0,153)';
                        ctx.fill();

                    });

                    if(gioState.tempPath != null && gioState.tempPath.nodes.length > 0)
                        gioState.tempPath.draw(gioState.ctx);
                }
                else
                {
                    gioState.tempPath.animate(gioState.ctx);
                }

            }

            // disegno la selezione intorno al selected_item
            if(gioState.selectedItem !== null && gioState.selectedItem !== gioState.tempArea)
            {
                console.log(gioState.selectedItem.color);
                ctx.strokeStyle = gioState.selectedItem.color;
                ctx.lineWidth = gioState.selectionWidth;
                let selection = gioState.selectedItem;
                ctx.strokeRect(selection.x, selection.y, selection.width, selection.height);
                ctx.lineWidth = 1;
            }
            
            if(gioState.tempArea != null)
            {
                ctx.setLineDash([6]);
                ctx.strokeStyle = 'rgb(0,0,0)';
                gioState.tempArea.draw(ctx);
            }

            if(gioState.currentHandle)
            {
                let posHandle = point(0,0);
                let tempArea = gioState.tempArea;
                switch (gioState.currentHandle)
                {
                    case 'topleft':
                        posHandle.x = tempArea.x;
                        posHandle.y = tempArea.y;
                        break;
                    case 'topright':
                        posHandle.x = tempArea.x + tempArea.width;
                        posHandle.y = tempArea.y;
                        break;
                    case 'bottomleft':
                        posHandle.x = tempArea.x;
                        posHandle.y = tempArea.y + tempArea.height;
                        break;
                    case 'bottomright':
                        posHandle.x = tempArea.x + tempArea.width;
                        posHandle.y = tempArea.y + tempArea.height;
                        break;
                    case 'top':
                        posHandle.x = tempArea.x + tempArea.width / 2;
                        posHandle.y = tempArea.y;
                        break;
                    case 'left':
                        posHandle.x = tempArea.x;
                        posHandle.y = tempArea.y + tempArea.height / 2;
                        break;
                    case 'bottom':
                        posHandle.x = tempArea.x + tempArea.width / 2;
                        posHandle.y = tempArea.y + tempArea.height;
                        break;
                    case 'right':
                        posHandle.x = tempArea.x + tempArea.width;
                        posHandle.y = tempArea.y + tempArea.height / 2;
                        break;
                }
                //ctx.globalCompositeOperation = 'xor';
                ctx.beginPath();
                ctx.arc(posHandle.x, posHandle.y, gioState.handlesSize, 0, 2 * Math.PI);
                ctx.fillStyle = 'rgb(0,143,10)';
                ctx.fill();
                //ctx.globalCompositeOperation = 'source-over';
            }
            ctx.setLineDash([0]);
            gioState.valid = true;
            ctx.restore();
        }
    };
}

function init()
{
    mainCanvas = new GioCanvas(document.getElementById('mainCanvas'));
    newAreaButton = document.getElementById('newAreaButton');
    deleteAreaButton = document.getElementById('deleteAreaButton');
    pathButton = document.getElementById('pathButton');

    let img = new Image();
    img.src = 'img/mappa-dipartimento.jpg';
    mainCanvas.backgroundImage = img;

    doRequest('GET','rooms',null, function (response) {
        response = JSON.parse(response);
        let table = document.getElementById('roomTable');
        response.forEach(function(room)
        {
            let newShape = new Room(room.id_room, room.x, room.y, room.width, room.height, room.color);
            newShape.number = room.number;
            newShape.name = room.name;
            newShape.type = room.type;
            mainCanvas.addShape(newShape);

            let row = table.insertRow(-1); // inserito in ultima posizione
            let number = row.insertCell(0);
            let name = row.insertCell(1);
            let action1 = row.insertCell(2);
            let action2 = row.insertCell(3);

            let index = document.createElement("input");
            index.setAttribute('type', 'hidden');
            index.setAttribute('name', 'index');
            index.setAttribute('value',room.id_room);
            row.appendChild(index);
            number.innerHTML = toTitleCase(room.number);
            name.innerHTML = (room.name !== null) ? toTitleCase(room.name) : (room.type + " " + room.number);

            let position = new Image();
            position.src = "img/pin.png";
            position.style.cursor = "pointer";
            position.addEventListener('click', function () {
                let tr = this.parentElement.parentElement;
                hidePopup();
                let shapes = mainCanvas.shapes;
                let room_id = parseInt(tr.children[4].value);
                let room = shapes.find(function (el) { return el.id === room_id});
                animateOfficeAndLocation(mainCanvas.ctx,room,null,'rgb(0,143,10)', null);
            });

            let path = new Image();
            path.src = "img/passi.png";
            path.style.cursor = "pointer";
            path.addEventListener('click', function ()
            {
                let tr = this.parentElement.parentElement;
                hidePopup();
                let shapes = mainCanvas.shapes;
                let room_id = parseInt(tr.children[4].value);
                let room = shapes.find(function (el) { return el.id === room_id});
                mainCanvas.tempPath = new Path();
                mainCanvas.tempPath.begin = shapes.find(function (el) {
                    return el.name === "PORTINERIA"
                });

                minPath(mainCanvas.tempPath.begin, room);
                changeInfoText("Ecco dove si trova la stanza " + room.number);
            });

            action1.appendChild(position);
            action2.appendChild(path);
            row.style.display = "none";
        });

        newAreaButton.onclick = function () {
            hidePopup();
            hidePin();
            openForm("", "","","rgb(255,0,0)");
            changeInfoText('Dopo aver posizionato la nuova area, fai doppio click su di essa per confermarla o premi ESC per annullare');
        };

        deleteAreaButton.onclick = function () {
            hidePopup();
            hidePin();
            mainCanvas.deleting = true;
            disableButton(true);
            changeInfoText('Fai click su un area per eliminarla o premi ESC per annullare');
            mainCanvas.valid = false;
            mainCanvas.draw();
        };

        pathButton.onclick = function () {
            hidePopup();
            hidePin();
            switch (mainCanvas.pathing)
            {
                case false:
                {
                    mainCanvas.pathing = 'selectBegin';
                    newAreaButton.disabled = true;
                    deleteAreaButton.disabled = true;

                    changeInfoText('Seleziona la stanza da cui partire');
                    pathButton.innerText = 'Confirm Path';
                    break;
                }

                case 'selectBegin':
                {
                    changeInfoText('Prima seleziona il punto di partenza!');
                    break;
                }

                case 'selectEnd':
                {
                    changeInfoText('Prima seleziona il punto di arrivo!');
                    break;
                }

                case 'drawPath':
                {
                    changeInfoText("Disegna un percorso fino alla stanza selezionata!");
                    break;
                }

                case 'confirm':
                    mainCanvas.validatePath();

                case 'showPath':
                {
                    mainCanvas.pathing = false;
                    mainCanvas.tempPath = null;
                    pathButton.innerText = "Start Path";
                    disableButton(false);
                    break;
                }
            }
            mainCanvas.valid = false;
            mainCanvas.draw();
        }

         heatmapButton.onclick = function () { //WoT
            let len = mainCanvas.shapes.length;
            for(let i=0; i<len; i++)
            {
                let shape = mainCanvas.shapes[i];
                let number = shape.number;
                let color = shape.color;

                shape.color = '#7E8987';
                getRoomEnv(number,function(data){


                    if(data["temperatureL"] == "HIGH") shape.color = "#FC9F5B"
                    if(data["temperatureL"] == "VERY_HIGH") shape.color = "#BC412B";
                    else if(data["temperatureL"] == "LOW") shape.color = "#05A8AA";
                    if(data["temperatureL"] == "VERY_LOW") shape.color = "#247BA0";
                    else if(data["temperatureL"] == "MEDIUM") shape.color = "#9DBF9E";

                });

                shape.drawBorder(mainCanvas.ctx);
                shape.drawAndFill(mainCanvas.ctx);
                shape.color = color
            }
        };


        lightmapButton.onclick = function () { //WoT
            let len = mainCanvas.shapes.length;
            for(let i=0; i<len; i++)
            {
                let shape = mainCanvas.shapes[i];
                let number = shape.number;
                let color = shape.color;

                shape.color = "#808080";
                getRoomEnv(number,function(data){


                    if(data["lightL"] == "HIGH") shape.color = "#BC412B";
                    else if(data["lightL"] == "LOW") shape.color = "#247BA0";
                    else if(data["lightL"] == "MEDIUM") shape.color = "#7CFC00";

                });

                shape.drawBorder(mainCanvas.ctx);
                shape.drawAndFill(mainCanvas.ctx);
                shape.color = color
            }
        };


    });


    doRequest('GET','users',null,function (response) {
        response = JSON.parse(response);
        users = response.slice();
        response = null;
        let table = document.getElementById('userTable');
        users.forEach(function (user)
        {
            let row = table.insertRow(-1); // inserito in ultima posizione
            let name = row.insertCell(0);
            let surname = row.insertCell(1);
            let presence = row.insertCell(2);
            let index = document.createElement("input");
            index.setAttribute('type', 'hidden');
            index.setAttribute('name', 'index');
            index.setAttribute('value',users.indexOf(user).toString());
            row.appendChild(index);

            let img = new Image();
            let text = toTitleCase(user.name) + " " + toTitleCase(user.surname)  + " ";
            let officeColor = 'rgb(139,0,0)';
            if(user.last_location)
            {
                if(user.last_location === user.office) // in ufficio
                {
                    img.src = "img/green.png";
                    text += "<b>&egrave;</b> nel suo ufficio.";
                    officeColor = 'rgb(0,143,10)';
                }
                else
                {
                    img.src = "img/yellow.png"; // non in ufficio, ma conosco la location
                    text += "<b>non &egrave;</b> nel suo ufficio.<br/> Si trova nella <b>stanza " + user.location_number + "</b>";
                    if(user.location_name) text += ": " + user.location_name;
                    officeColor = 'rgb(204,204,0)';
                }
            }
            else
            {
                img.src = "img/red.png"; // non in ufficio, non so dove si trovi
                text += "<b>non &egrave;</b> nel suo ufficio (" + user.office_number + ").";
            }

            presence.appendChild(img);
            name.innerHTML = toTitleCase(user.name);
            surname.innerHTML = toTitleCase(user.surname);
            row.style.display = "none";
            row.addEventListener('click',function () {
                hidePopup();
                let user = users[this.children[3].value];
                let shapes = mainCanvas.shapes;
                let office = shapes.find(function (el) {return el.id === user.office});
                let location = shapes.find(function (el) {return el.id === user.last_location});

                if (office === location)
                    animateOfficeAndLocation(mainCanvas.ctx, office, null, officeColor, null);
                else
                    animateOfficeAndLocation(mainCanvas.ctx, office, location, 'rgb(139,0,0)', 'rgb(204,204,0)');
                changeInfoText(text, officeColor);
            });
        });
    });
}

function checkConnection()
{
    infoDiv = document.getElementById('infoDiv').getElementsByTagName('p')[0];
    reloadButton = document.getElementById('reloadButton');

    reloadButton.addEventListener('click', function () {
        window.location.reload();
    });
    doRequest('GET','nodes', null,
        function (response)
        {
            response = JSON.parse(response);
            response.forEach(function (node) {
                circles.push(node); });

            init();
        },
        function(response)
        {
            let text ="Errore nella connessione con GioMap";
            if(response)
            {
                response = JSON.parse(response);
                text += " " + response.message;
            }

            text = "<h3>" + text + "</h3>";

            changeInfoText(text, "#FF0000");
        });
}

function animateOfficeAndLocation(ctx, office, location, officeColor, locationColor)
{
    if(roomInterval !== null)
        clearInterval(roomInterval);

    if(pathInterval !== null)
    {
        clearInterval(pathInterval);
        mainCanvas.pathing = false;
    }

    mainCanvas.valid = false;
    mainCanvas.draw();

    let opacity = 0;
    let delta = 0.1;
    let rgbaOffice, rgbaLocation;
    let i = 0;
    if(!officeColor) officeColor = 'rgb(255,0,0)';
    if(!locationColor) locationColor = 'rgb(255,0,0)';

    rgbaOffice = officeColor.replace('rgb','rgba').replace(')',','+ opacity +')');
    rgbaLocation = locationColor.replace('rgb','rgba').replace(')',','+ opacity +')');
    let dv = document.getElementById("canvas-wrap");
    if(location)
        dv.scrollTo(location.x - 200, 0);
    if(office)
    {
        if(!location)
            dv.scrollTo(office.x - 200, 0);
    }

    if(office || location)
    {
        roomInterval = setInterval(function ()
        {
            //mainCanvas.valid = false;
            //mainCanvas.draw();
            if(office)
                office.fill(ctx, opacity, rgbaOffice);

            if(location)
                location.fill(ctx, opacity, rgbaLocation);

            opacity += delta;
            if(opacity > 0.99 || opacity < 0.1)
            {
                delta *= -1;
                i++;
            }

            if(i===5)
            {
                // ripristino i colori che le aree avevano prima dell'animazione
                clearInterval(roomInterval);
            }

        }, 50);
    }
}

function setAreaInfo()
{
    if(mainCanvas.tempArea !== null)
    {
        mainCanvas.validateShape();
        closeForm();
        return;
    }
    mainCanvas.isNew = true;
    mainCanvas.unselectItem();
    closeForm();
    disableButton(true);

    mainCanvas.drawing = true;
    mainCanvas.valid = false;
    mainCanvas.draw();
}

function changeType()
{
    let type = document.getElementById('area_type').value;
    let color = "#000000";
    switch (type) {
        case "LAB":
        {
            color = "#0433ff";
            break;
        }
        case "OFFICE":
        {
            color = "#ff0000";
            break;
        }
        case "CONFERENCE":
        {
            color = "#942192";
            break;
        }
        case "STAIRS":
        {
            color = "#00f900";
            break;
        }
        case "WC":
        {
            color = "#fffb00";
            break;
        }
        case "OTHER":
        {
            color = "#aa7942";
            break;
        }

    }

    document.getElementById('area_color').value = color;
}

function openForm(number, name, type, color)
{
    document.getElementById('areaForm').style.display = 'block';
    document.getElementById('area_number').value = number;
    document.getElementById('area_name').value = name;
    document.getElementById('area_type').value = type;
    document.getElementById('area_color').value = color;
    disableButton(true);
    hidePopup();

}

function closeForm()
{
    document.getElementById('areaForm').style.display = 'none';
    if(mainCanvas.tempArea !== null && !mainCanvas.drawing)
    {
        mainCanvas.tempArea.x = mainCanvas.oldPos.x;
        mainCanvas.tempArea.y = mainCanvas.oldPos.y;
        mainCanvas.shapes.push(mainCanvas.tempArea);
        mainCanvas.tempArea = null;
        mainCanvas.oldPos = null;
    }
    mainCanvas.unselectItem();
    mainCanvas.valid = false;
    mainCanvas.draw();
    disableButton(false);
}

function copyNumber()
{
    document.getElementById('area_name').value = document.getElementById('area_number').value;
}

function filterTable(tableId, inputId) {
    let input, filter, table, tr, firstTd, secondTd, i, txtFirst, txtSecond;
    input = document.getElementById(inputId);
    filter = input.value.toUpperCase();
    table = document.getElementById(tableId);
    tr = table.getElementsByTagName("tr");

    for (i = 0; i < tr.length; i++) {
        firstTd = tr[i].getElementsByTagName("td")[0];
        secondTd = tr[i].getElementsByTagName("td")[1];
        if (firstTd && secondTd) {
            txtFirst = firstTd.textContent || firstTd.innerText;
            txtSecond = secondTd.textContent || secondTd.innerText;
            if ((txtFirst.toUpperCase().indexOf(filter) > -1 || txtSecond.toUpperCase().indexOf(filter) > -1) && filter.trim() !== "")
                tr[i].style.display = "";
            else
                tr[i].style.display = "none";
        }
    }
}

function changeInfoText(text, color)
{
    if(text === "")
    {
        infoDiv.innerHTML = text;
        return;
    }

    let stl = infoDiv.style;
    infoDiv.style.opacity = "0";
    infoDiv.innerHTML = text;
    if(color)
        infoDiv.style.color = color;
    let interval = setInterval(function ()
    {
        stl.opacity = Number(stl.opacity)+0.1;
        if(stl.opacity >= 1)
            clearInterval(interval);
    }, 100);
}

function toTitleCase(str) {
    return str.replace(/\w\S*/g,
        function(txt) {
            return txt.charAt(0).toUpperCase() + txt.substr(1).toLowerCase();}
    );
}

function disableButton(disabled)
{
    if(!disabled)
        changeInfoText("");
    newAreaButton.disabled = disabled;
    deleteAreaButton.disabled = disabled;
    pathButton.disabled = disabled;
}

window.addEventListener('keydown', function (e) {
    if (e.defaultPrevented) {
        return; // Should do nothing if the default action has been cancelled
    }

    if( e.keyCode === 27)
    {
        if(pathInterval !== null)
            clearInterval(pathInterval);

        if(roomInterval !== null)
            clearInterval(roomInterval);

        if(mainCanvas.deleting) //deleting area
            mainCanvas.deleting = false;

        if(mainCanvas.drawing)  // drawing new area
            mainCanvas.drawing = false;

        if(mainCanvas.tempArea)  // drawing new area
        {
            closeForm();
            mainCanvas.tempArea = null;
        }

        if(mainCanvas.dragging)
            mainCanvas.dragging = false;

        if(mainCanvas.pathing)
        {
            mainCanvas.pathing = false;
            mainCanvas.tempPath = null;
            pathButton.innerText = 'Start Path';

        }
        closeForm();
        changeInfoText("");
    }
});

window.onload = checkConnection;



