private static List<RankerResult>? GetRandomWeightedKnobs(IList<RankerResult> rankedResults, Experience experienceConfiguration)
{
    int topKnobs = experienceConfiguration.TopWeightedKnobs ?? 1;
    var weightedRankedResults = rankedResults.Where(r => r?.Knob?.Weight != null).ToList();

    if (!weightedRankedResults.SafeAny())
    {
        // If there is no knob returned with weight, then return the top score knob
        return rankedResults.OrderByDescending(r => r?.Score).Take(Math.Min(topKnobs, rankedResults.Count)).ToList();
    }

    if (weightedRankedResults.Count == 1)
    {
        return weightedRankedResults;
    }

    // Step 3: Random sampling
    int numDesiredKnobs = Math.Min(topKnobs, weightedRankedResults.Count); // TODO: This should be coming from layout config
    Random random = new Random();
    var targetScopes = new List<RankerResult>();

    for (int i = 0; i < numDesiredKnobs && targetScopes.Count < numDesiredKnobs; i++)
    {
        double totalWeight = (double)weightedRankedResults.Sum(r => r?.Knob?.Weight ?? 0);
        var normalizedWeightedKnobs = new Dictionary<string, RankerResult>();

        foreach (var weightedKnob in weightedRankedResults)
        {
            if (weightedKnob?.Knob?.Weight > 0 && totalWeight != 0)
            {
                double normalizedWeight = (double)(weightedKnob.Knob.Weight / totalWeight);
                string knobNameWeighted = normalizedWeight.ToString() + '_' + weightedKnob.KnobId;
                normalizedWeightedKnobs.TryAdd(knobNameWeighted, weightedKnob);
            }
        }

        double randomValue = random.NextDouble(); // Generate random number between 0 and 1

        // Compare random value with normalized weights
        double currentWeight = 0;

        foreach (var normalizedKnobs in normalizedWeightedKnobs.OrderBy(kv => kv.Key))
        {
            if (double.TryParse(normalizedKnobs.Key.Split('_')[0], out var normalizedWeight))
            {
                currentWeight += normalizedWeight;

                if (randomValue <= currentWeight)
                {
                    targetScopes.Add(normalizedKnobs.Value);
                    var knobId = normalizedKnobs.Value.Knob?.Id;
                    int index = weightedRankedResults.FindIndex(x => x.Knob.Id == knobId);
                    weightedRankedResults.RemoveAt(index);

                    break;
                }
            }
        }

        if (targetScopes.Count < numDesiredKnobs && weightedRankedResults.Count == 1)
        {
            targetScopes.Add(weightedRankedResults[0]);
        }
    }

    return targetScopes;
}