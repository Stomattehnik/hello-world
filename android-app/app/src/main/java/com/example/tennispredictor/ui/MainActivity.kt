package com.example.tennispredictor.ui

import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.PaddingValues
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.verticalScroll
import androidx.compose.material3.Button
import androidx.compose.material3.Card
import androidx.compose.material3.ExperimentalMaterial3Api
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.OutlinedTextField
import androidx.compose.material3.Scaffold
import androidx.compose.material3.Text
import androidx.compose.material3.TopAppBar
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.Modifier
import androidx.compose.ui.res.stringResource
import androidx.compose.ui.text.input.KeyboardOptions
import androidx.compose.ui.text.input.KeyboardType
import androidx.compose.ui.unit.dp
import com.example.tennispredictor.R
import com.example.tennispredictor.model.MatchPrediction
import com.example.tennispredictor.model.PlayerStats
import com.example.tennispredictor.model.winProbability

class MainActivity : ComponentActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContent {
            MaterialTheme {
                TennisPredictorApp()
            }
        }
    }
}

private data class PlayerInputState(
    val name: String = "",
    val ranking: String = "",
    val serve: String = "",
    val returnStat: String = "",
    val surface: String = "",
    val form: String = "",
)

private data class FieldValidation<T>(
    val value: T?,
    val error: String?,
)

private data class PlayerValidation(
    val nameError: String?,
    val ranking: FieldValidation<Int>,
    val serve: FieldValidation<Double>,
    val returnStat: FieldValidation<Double>,
    val surface: FieldValidation<Double>,
    val form: FieldValidation<Double>,
) {
    val isValid: Boolean
        get() = nameError == null &&
            ranking.error == null &&
            serve.error == null &&
            returnStat.error == null &&
            surface.error == null &&
            form.error == null

    fun toPlayerStats(state: PlayerInputState): PlayerStats? {
        if (!isValid) return null
        return PlayerStats(
            name = state.name.trim(),
            ranking = ranking.value!!,
            servePointsWon = serve.value!!,
            returnPointsWon = returnStat.value!!,
            surfaceWinPct = surface.value!!,
            recentForm = form.value!!,
        )
    }
}

private data class ValidationMessages(
    val invalidNumber: String,
    val valueRangeError: String,
    val nameRequired: String,
    val rankingPositive: String,
)

private fun validatePlayerInput(
    state: PlayerInputState,
    messages: ValidationMessages,
): PlayerValidation {
    val nameError = if (state.name.isBlank()) messages.nameRequired else null

    val rankingValidation = parseRanking(state.ranking, messages)
    val serveValidation = parseBoundedDouble(state.serve, messages)
    val returnValidation = parseBoundedDouble(state.returnStat, messages)
    val surfaceValidation = parseBoundedDouble(state.surface, messages)
    val formValidation = parseBoundedDouble(state.form, messages)

    return PlayerValidation(
        nameError = nameError,
        ranking = rankingValidation,
        serve = serveValidation,
        returnStat = returnValidation,
        surface = surfaceValidation,
        form = formValidation,
    )
}

private fun parseRanking(text: String, messages: ValidationMessages): FieldValidation<Int> {
    if (text.isBlank()) {
        return FieldValidation(null, messages.invalidNumber)
    }
    val value = text.toIntOrNull()
        ?: return FieldValidation(null, messages.invalidNumber)
    if (value <= 0) {
        return FieldValidation(null, messages.rankingPositive)
    }
    return FieldValidation(value, null)
}

private fun parseBoundedDouble(text: String, messages: ValidationMessages): FieldValidation<Double> {
    if (text.isBlank()) {
        return FieldValidation(null, messages.invalidNumber)
    }
    val normalised = text.replace(',', '.')
    val value = normalised.toDoubleOrNull()
        ?: return FieldValidation(null, messages.invalidNumber)
    if (value !in 0.0..1.0) {
        return FieldValidation(null, messages.valueRangeError)
    }
    return FieldValidation(value, null)
}

@OptIn(ExperimentalMaterial3Api::class)
@Composable
private fun TennisPredictorApp() {
    Scaffold(
        topBar = {
            TopAppBar(title = { Text(text = stringResource(id = R.string.app_name)) })
        },
    ) { padding ->
        TennisPredictorScreen(contentPadding = padding)
    }
}

@Composable
private fun TennisPredictorScreen(contentPadding: PaddingValues) {
    var playerOneState by remember {
        mutableStateOf(
            PlayerInputState(
                name = "Iga Świątek",
                ranking = "1",
                serve = "0.62",
                returnStat = "0.46",
                surface = "0.80",
                form = "0.90",
            )
        )
    }
    var playerTwoState by remember {
        mutableStateOf(
            PlayerInputState(
                name = "Elena Rybakina",
                ranking = "4",
                serve = "0.58",
                returnStat = "0.41",
                surface = "0.74",
                form = "0.85",
            )
        )
    }
    var prediction by remember { mutableStateOf<MatchPrediction?>(null) }

    val messages = ValidationMessages(
        invalidNumber = stringResource(R.string.invalid_number),
        valueRangeError = stringResource(R.string.value_range_error),
        nameRequired = stringResource(R.string.name_required),
        rankingPositive = stringResource(R.string.ranking_positive_error),
    )

    val playerOneValidation = validatePlayerInput(playerOneState, messages)
    val playerTwoValidation = validatePlayerInput(playerTwoState, messages)

    Column(
        modifier = Modifier
            .fillMaxSize()
            .verticalScroll(rememberScrollState())
            .padding(contentPadding)
            .padding(16.dp),
        verticalArrangement = Arrangement.spacedBy(16.dp),
    ) {
        PlayerCard(
            title = stringResource(R.string.player_one),
            state = playerOneState,
            validation = playerOneValidation,
            onStateChange = { playerOneState = it },
        )
        PlayerCard(
            title = stringResource(R.string.player_two),
            state = playerTwoState,
            validation = playerTwoValidation,
            onStateChange = { playerTwoState = it },
        )

        Button(
            onClick = {
                val playerOne = playerOneValidation.toPlayerStats(playerOneState)
                val playerTwo = playerTwoValidation.toPlayerStats(playerTwoState)
                if (playerOne != null && playerTwo != null) {
                    prediction = winProbability(playerOne, playerTwo)
                }
            },
            enabled = playerOneValidation.isValid && playerTwoValidation.isValid,
            modifier = Modifier.fillMaxWidth(),
        ) {
            Text(text = stringResource(R.string.calculate))
        }

        prediction?.let { result ->
            PredictionResult(prediction = result)
        }
    }
}

@Composable
private fun PlayerCard(
    title: String,
    state: PlayerInputState,
    validation: PlayerValidation,
    onStateChange: (PlayerInputState) -> Unit,
) {
    Card(modifier = Modifier.fillMaxWidth()) {
        Column(
            modifier = Modifier
                .padding(16.dp),
            verticalArrangement = Arrangement.spacedBy(12.dp),
        ) {
            Text(text = title, style = MaterialTheme.typography.titleMedium)
            OutlinedTextField(
                value = state.name,
                onValueChange = { onStateChange(state.copy(name = it)) },
                label = { Text(text = title) },
                isError = validation.nameError != null,
                supportingText = {
                    validation.nameError?.let { Text(text = it, color = MaterialTheme.colorScheme.error) }
                },
                modifier = Modifier.fillMaxWidth(),
                singleLine = true,
            )
            OutlinedNumberField(
                value = state.ranking,
                label = stringResource(R.string.ranking_hint),
                errorMessage = validation.ranking.error,
                keyboardType = KeyboardType.Number,
                onValueChange = { onStateChange(state.copy(ranking = it)) },
            )
            OutlinedNumberField(
                value = state.serve,
                label = stringResource(R.string.serve_hint),
                errorMessage = validation.serve.error,
                keyboardType = KeyboardType.Decimal,
                onValueChange = { onStateChange(state.copy(serve = it)) },
            )
            OutlinedNumberField(
                value = state.returnStat,
                label = stringResource(R.string.return_hint),
                errorMessage = validation.returnStat.error,
                keyboardType = KeyboardType.Decimal,
                onValueChange = { onStateChange(state.copy(returnStat = it)) },
            )
            OutlinedNumberField(
                value = state.surface,
                label = stringResource(R.string.surface_hint),
                errorMessage = validation.surface.error,
                keyboardType = KeyboardType.Decimal,
                onValueChange = { onStateChange(state.copy(surface = it)) },
            )
            OutlinedNumberField(
                value = state.form,
                label = stringResource(R.string.form_hint),
                errorMessage = validation.form.error,
                keyboardType = KeyboardType.Decimal,
                onValueChange = { onStateChange(state.copy(form = it)) },
            )
        }
    }
}

@Composable
private fun OutlinedNumberField(
    value: String,
    label: String,
    errorMessage: String?,
    keyboardType: KeyboardType,
    onValueChange: (String) -> Unit,
) {
    OutlinedTextField(
        value = value,
        onValueChange = onValueChange,
        label = { Text(text = label) },
        keyboardOptions = KeyboardOptions(keyboardType = keyboardType),
        isError = errorMessage != null,
        supportingText = {
            errorMessage?.let { Text(text = it, color = MaterialTheme.colorScheme.error) }
        },
        modifier = Modifier.fillMaxWidth(),
        singleLine = true,
    )
}

@Composable
private fun PredictionResult(prediction: MatchPrediction) {
    Card(modifier = Modifier.fillMaxWidth()) {
        Column(
            modifier = Modifier.padding(16.dp),
            verticalArrangement = Arrangement.spacedBy(8.dp),
        ) {
            Text(
                text = prediction.playerOne.name,
                style = MaterialTheme.typography.titleMedium,
            )
            Text(
                text = stringResource(
                    id = R.string.probability_result,
                    prediction.probabilityOne * 100,
                ),
            )
            Text(
                text = stringResource(
                    id = R.string.quality_score,
                    prediction.playerOne.qualityScore(),
                ),
                style = MaterialTheme.typography.bodySmall,
            )
            Spacer(modifier = Modifier.height(8.dp))
            Text(
                text = prediction.playerTwo.name,
                style = MaterialTheme.typography.titleMedium,
            )
            Text(
                text = stringResource(
                    id = R.string.probability_result,
                    prediction.probabilityTwo * 100,
                ),
            )
            Text(
                text = stringResource(
                    id = R.string.quality_score,
                    prediction.playerTwo.qualityScore(),
                ),
                style = MaterialTheme.typography.bodySmall,
            )
        }
    }
}
