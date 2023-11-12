Feature: Tools functionality

  Scenario: Insert testplan to database
    Given list of files
    When we load each file
    And insert it to database
    Then we have saved videos data in database
    