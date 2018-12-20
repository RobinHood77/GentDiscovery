// settings
var defaultHintTimeout = 600 // seconds
var distanceThreshold = 50 // meters

// demo mode overrides
var url = new URL(window.location.href)
if (url.searchParams.get("mode") == "demo") {
    defaultHintTimeout = 10 // seconds
    distanceThreshold = 1000 // meters
}

var progress, riddles, currentRiddle
var timerSeconds
var questionText, hintButton, answerButton
var timerInterval, distanceInterval

// prevent asking twice for location if a request is pending
var isAskingDistance = false

$(document).ready(function() {
    questionText = document.getElementById("questionText")
    initButtons()
    initIntervals()
    getProgress()
    updateRiddle()
});

function initButtons() {
    hintButton = document.getElementById("hintButton")
    answerButton = document.getElementById("answerButton")

    $("#hintButton").click(showHint);
    $("#answerButton").click(goToNextRiddle);
    $("#homeButton").click(returnToHome);
}

function initIntervals() {
    resetTimer()
    resetDistance()
}

function getProgress() {
    progress = getCookie("progress")
    progress = typeof progress == "string" ? parseInt(progress, 10) : 0
}

function updateRiddle() {
    currentRiddle = riddles[progress]
    questionText.innerHTML = currentRiddle.question
}

function goToNextRiddle() {
    progress++
    setCookie("progress", progress)
    if (progress >= riddles.length) {
        alert("Je hebt het einde bereikt!")
        returnToHome()
    }
    else {
        updateRiddle()
        deleteCookie("timerSeconds")
        resetTimer()
        resetDistance()
    }
}

function showHint() {
    $("#hintImage").attr("src", currentRiddle.hintImageUrl);
}

function returnToHome() {
    deleteCookie("progress")
    deleteCookie("timerSeconds")
    deleteCookie("seed")
    window.location.href = "../index.html"
}

function resetTimer() {
    $("#hintButton").prop("disabled", true);
    hintButton.innerHTML = "Hint over //://"

    timerSeconds = getCookie("timerSeconds")
    timerSeconds = typeof timerSeconds == "string" ? parseInt(timerSeconds, 10) : defaultHintTimeout

    clearInterval(timerInterval)

    updateTimer()
    timerInterval = setInterval(updateTimer, 1000)
}

function updateTimer() {
    minutes = Math.floor(timerSeconds / 60)
    seconds = timerSeconds % 60
    if (timerSeconds % 10 == 0) {
        setCookie("timerSeconds", timerSeconds)
    }
    if (timerSeconds < 0) {
        $("#hintButton").prop("disabled", false);
        hintButton.innerHTML = "Toon hint"
    }
    else {
        timerSeconds--
        hintButton.innerHTML = "Hint over " + (minutes < 10 ? "0" : "") + minutes + ":" + (seconds < 10 ? "0" : "") + seconds
    }
}

function resetDistance() {
    $("#answerButton").prop("disabled", true);
    answerButton.innerHTML = "Antwoord in ... m"

    clearInterval(distanceInterval)

    updateDistance()
    distanceInterval = setInterval(updateDistance, 1000)
}

function updateDistance() {
    if (navigator.geolocation) {
        if (!isAskingDistance) {
            isAskingDistance = true
            navigator.geolocation.getCurrentPosition(updateDistanceCallback);
        }
    }
    else {
        answerButton.innerHTML = "Antwoord in ... m"
        console.error("Geolocation is not supported on this device!")
    }
}

function updateDistanceCallback(position) {
    avgLatitude = (currentRiddle.latitude + position.coords.latitude) / 2
    dLatitude = currentRiddle.latitude - position.coords.latitude
    dLongitude = currentRiddle.longitude - position.coords.longitude
    dX = dLatitude * 40008000 / 360
    dY = dLongitude * Math.cos(avgLatitude * Math.PI / 180) * 40075160 / 360

    meters = Math.round(Math.sqrt(dX * dX + dY * dY))

    if (meters <= distanceThreshold) {
        $("#answerButton").prop("disabled", false);
        answerButton.innerHTML = "Volgende vraag"

        clearInterval(distanceInterval)
        
        alert("Je hebt het doel \"" + currentRiddle.answer + "\" bereikt!")
    }
    else {
        answerButton.innerHTML = "Antwoord in " + meters + "m"
    }
    isAskingDistance = false
}


