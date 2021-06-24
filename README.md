# Text Mining and Signal Extraction with JPM Earnings Call Transcript

Business Value-Add
------------------
An earnings call is a teleconference, or webcast, in which a public company discusses the financial results of a reporting period. It is of utmost importance to investors to assess the management's presentation and get a sense of the company's future performance. Therefore, creating a machine learning system that can quickly analyse and evaluate the sentiment of a EC transcript can be profitable and useful to parties of interest. In this project we extracted both textual and numerical information from JP Morgan's earnings call transcripts and created a scalable method to predict future movement of stock prices.

Short Model Description
-----------------------
Our goal was to predict the effect that the EC had on JP Morgan's stock price. In order to capture that effect we modeled our response feature as the change in slope of the stock price before and after the call. To predict this, we used two predicting features which we extracted from the transcript: text score and EPS spread. The former metric captured the performance of the company on a specific quarter based on textual analysis and the latter measured the gap between the consensus expected EPS and realized EPS reported on the call.
Data Preprocessing
In this section we will discuss the preprocessing we applied to the three variables of interest as mentioned above.

 Price Trend
 -------------
The response feature, the change of the price slope before and after the call, was created from the historical stock price using a multi-step approach. We first identified the date of the earning call and extracted out the 5-day price changes before and after the date. Using these 5-day prices we then performed a time-series linear regression to find the linear coefficient and used it as the price trend. After performing the regression steps for both before and after 5-day prices, we calculated the trend spread by simply subtracting the after trend with before trend.
Transcript Cleaning
We made the assumption in our model that not all speakers' words are of equal importance. More specifically, we assumed that in order to assess the company’s performance it suffices to focus on the words of the CEO and CFO. We therefore filtered out all the other speakers present in the call (such as the call operator, analysts, etc.)

Earnings Per Share Spread
------------------------
The other predicting feature, EPS spread, was created by subtracting the realized EPS announced during the earnings call by the corresponding consensus expected EPS.

Methodology
------------
Text Statistical Analysis
In order to get a better sense of the contents of EC transcripts we performed a textual statistical analysis. More specifically, we examined the frequency of words that appear in the JP Morgan transcripts and used word cloud and Zipf’s curve as visualization.
As the first step, we did a preliminary cleaning to the text in order to remove high frequency words with no particular meaning such as stopwords and the names of the speakers. We then displayed the text frequency using the Zipf’s curve.
As Zipf’s Law stated, the frequency of any word is inversely proportional to its rank in the frequency table. In other words, the occurrence of the most frequent word should be approximately twice as often as that of the second most frequent word. In the graph presented below, the red line in the plot shows the expected word frequency and the blue bar shows the actual word frequency, which indicates that several actual occurrences of words did not strictly follow Zipf’s distribution in our case.
