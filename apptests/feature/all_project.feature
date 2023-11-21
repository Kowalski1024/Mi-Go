Feature: General purpose of project and parts of it
  As a    [user]
  I want  [to test my speech-to-text model]
  So that [I use Mi-Go to evaluate and compare the accuracy of speech-to-text models]
  
  Scenario: Testplan generator must generate test plans in JSON format
    Given specific arguments for getting video that user want
    And filtering criteria
    When generate testplan
    Then we get requested videos

  Scenario: TestRunner must execute tests on a testplan, prepare the data for testing, run the tests, and store the results in a database
    Given testplan
    When register tests and trigger it
    Then results store in database and JSON file
  
  Scenario: TranscriptTest runs model and compares its output to the yt transcript
    Given Given arguments for a particular TranscriptTest
    When we turn on model 
    And get yt transciption
    And make difference
    Then we get compared data



