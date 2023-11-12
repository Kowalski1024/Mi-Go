Feature: Generators functionality
  As a    [user of this simple api interface]
  I want  [make crud operations like get videos or videos info from yt api]
  So that [interesting to me data]

  Scenario: Returns video details from youtube api
    Given we have videos list
    When we make request to youtube api
    Then we get dict with yt videos details

  Scenario: Returns categories that can be associated with YouTube videos
    Given we have regionCode for filter categories available in this region and hl for specify language of return data
    When we make request to youtube api
    Then we get dict with yt videos categories
  
  Scenario: Returns assignable categories from youtube api
    Given we have regionCode for filter categories available in this region and hl for specify language of return data
    When we make request to youtube api and filter received data when it have assignable == True
    Then return filtered data in dict

  Scenario: Returns assignable categories from youtube api
    Given we have regionCode for filter categories available in this region and hl for specify language of return data
    When we make request to youtube api 
    And filter received data when it have assignable == True
    Then return filtered data in dict

  Scenario: Perform a search request with valid parameters
    Given a YouTube API search request with parameters
    When the search request is executed
    Then return searched data in dict

  Scenario: Make operations on data for filtering only necessary data for testplan
    Given some results from youtube api 
    And wanting to extract only few info from this results
    When we iterate over all data 
    And remove unnecessary keys in data
    Then return filtered data

  Scenario: We want to add additional info about videos
    Given videos 
    When we collect ids of videos 
    And make request for info
    Then we extend video info by duration 
    And we extend video info by audio language

  Scenario: Make transcript for every video in data
    Given list of videos
    When we collect ids of videos
    And transcibe each video
    Then we add to video info manual transcript
    And we add to vide info auto generated transcript

  Scenario: Save videos info as json file
    Given videos infos list
    And destination path
    And category name 
    And actual data time 
    When we create directory and store video data
    Then we have saved data
  
  Scenario: We want to read commends from commendline 
    Given nothing 
    When we pass parsing specification as arguments 
    Then have ready prepared parser 

  
  Scenario: Generate proper testplan
    Given arguments for youtube api
    When we make request to api
    And filtering data only for testplan
    And add transcipt for videos
    And add additional info for each video
    Then return testplan