var userCoords = { lat: '', lng: '' };
function getLocation() {
    if (navigator.geolocation) {
        navigator.geolocation.getCurrentPosition(showPosition);

    } else {
        alert("Geolocation is not supported by this browser.");
    }
}

function showPosition(position) {
    userCoords.lat = position.coords.latitude;
    userCoords.lng = position.coords.longitude;
    console.log(userCoords);//Works
    document.getElementById("latitudeUsuario").value = userCoords.lat;
    document.getElementById("longitudeUsuario").value = userCoords.lng;
}