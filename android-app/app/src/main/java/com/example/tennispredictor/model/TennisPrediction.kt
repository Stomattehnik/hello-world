package com.example.tennispredictor.model

data class PlayerStats(
    val name: String,
    val ranking: Int,
    val servePointsWon: Double,
    val returnPointsWon: Double,
    val surfaceWinPct: Double,
    val recentForm: Double,
) {
    init {
        require(ranking > 0) { "ranking must be positive" }
        require(servePointsWon in 0.0..1.0) { "serve must be between 0 and 1" }
        require(returnPointsWon in 0.0..1.0) { "return must be between 0 and 1" }
        require(surfaceWinPct in 0.0..1.0) { "surface must be between 0 and 1" }
        require(recentForm in 0.0..1.0) { "form must be between 0 and 1" }
    }

    fun qualityScore(): Double {
        val rankingScore = (300 - ranking.coerceAtMost(300)) / 300.0
        return 0.30 * rankingScore +
            0.30 * servePointsWon +
            0.20 * returnPointsWon +
            0.10 * surfaceWinPct +
            0.10 * recentForm
    }
}

data class MatchPrediction(
    val playerOne: PlayerStats,
    val playerTwo: PlayerStats,
    val probabilityOne: Double,
    val probabilityTwo: Double,
)

fun winProbability(playerOne: PlayerStats, playerTwo: PlayerStats): MatchPrediction {
    val scoreOne = playerOne.qualityScore()
    val scoreTwo = playerTwo.qualityScore()
    val scale = 6.5
    val diff = (scoreOne - scoreTwo) * scale
    val probabilityOne = 1.0 / (1.0 + kotlin.math.exp(-diff))
    val probabilityTwo = 1.0 - probabilityOne
    return MatchPrediction(playerOne, playerTwo, probabilityOne, probabilityTwo)
}
