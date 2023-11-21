Feature: TestRunner functionality - Youtube implementation

  Scenario: Running YouTube Test Runner
    Given a YouTube Test Runner instance with valid parameters
    When the run method is called
    Then it should execute the testplan for the specified iterations

  Scenario: Saving testplan results
    Given a YouTube Test Runner instance with completed testplan results
    When the save_results method is called with the testplan results
    Then it should save the results to a JSON file

  Scenario: Generating video details from testplan
    Given a YouTube Test Runner instance with a valid testplan
    When the video_details method is called with the testplan
    Then it should return a generator of video details
  
  Scenario: Adding Runner specific arguments to parser
    Given an argument parser
    When the runner_args method is called with the parser
    Then it should add specific arguments related to the YouTube Test Runner

  Scenario: Checking transcriber and normalizer
    Given a YouTube Test Runner instance
    When the run method is called
    Then it should check if transcriber and normalizer are not None, otherwise log a warning

  Scenario: Handling Video Download Errors
    Given a YouTube Test Runner instance with a video that cannot be downloaded
    When the run method is called
    Then it should skip the video, log a warning, and continue with the next video

  Scenario: Handling transcription timeout errors
    Given a YouTube Test Runner instance with a video that times out during transcription
    When the run method is called
    Then it should skip the video, log a warning, and continue with the next video

  Scenario: Comparing transcripts and handling Errors
    Given a YouTube Test Runner instance with model and target transcripts
    When the run method is called
    Then it should compare the transcripts, handle errors, and continue with the next video if there's a comparison error

  Scenario: Handling Google API absence
    Given a YouTube Test Runner instance with iterations more than 1 and no Google API in the environment
    When the run method is called
    Then it should raise a ValueError indicating the absence of Google API and recommend setting iterations to 1 or adding Google API to the environment



