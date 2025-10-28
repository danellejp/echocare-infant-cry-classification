# Dataset Information

## Donate-A-Cry Corpus

**Source**: [https://github.com/gveres/donateacry-corpus](https://github.com/gveres/donateacry-corpus)

**Description**: 
The Donate-A-Cry Corpus is a publicly available dataset containing over 450 infant cry audio recordings collected from parents via a mobile application. It is designed to aid in identifying the needs of infants through their crying patterns.

### Dataset Characteristics
- **Total samples**: 457 recordings
- **Categories**: 5 (hungry, needs burping, belly pain, discomfort, tired)
- **Audio length**: 5-10 seconds per clip
- **Format**: .wav files
- **Sample rate**: Varies (16kHz - 44.1kHz)
- **Collection method**: Real-world, parent-reported labels
- **Age range**: 0-24 months

### Categories Used
For this project, I will merge the 5 original categories into 2:
- **Hungry**: "hungry" 
- **Discomfort**: "needs burping", "belly pain", "discomfort", "tired"

### Preprocessing Pipeline
1. Audio normalization
2. Resampling to 16kHz
3. Noise reduction
4. Mel-spectrogram generation
5. Train/validation/test split

## References
- Dataset Repository: https://github.com/gveres/donateacry-corpus

## Open Source Projects that used the Donate-A-Cry Corpus Dataset
https://github.com/martha92/babycry/
https://github.com/hamzakhalil798/Baby-Cry-Classification/
https://github.com/Aman-Vishwakarma1729/Automatic_Infant_Cry_Audio_Classification/
https://github.com/Mathanwarrior/Infant_cry_analysis_and_classification_using_CNN/

## Peer-Reviewed Papers that used the Donate-A-Cry Corpus Dataset
https://pmc.ncbi.nlm.nih.gov/articles/PMC10882089/
https://www.mdpi.com/2227-7080/13/4/130/