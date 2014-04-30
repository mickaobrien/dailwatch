<?php

function json_api_menu() {
    $items = array();
    $items['api/polls'] = array(
        'page callback' => 'polls',
        'page arguments' => array(2),
        'access arguments' => array('access content'),
        'access callback' => TRUE
    );

    $items['api/constituencies'] = array(
        'page callback' => 'constituencies',
        'access callback' => TRUE
    );

    $items['api/politicians'] = array(
        'page callback' => 'politicians',
        'access callback' => TRUE
    );

    $items['api/top-trumps'] = array(
        'page callback' => 'top_trumps',
        'access callback' => TRUE
    );
    return $items;
}

function api_call($sql, $args=array()) {
//Generic wrapper for API calls
    $result = db_query($sql,$args)->fetchAll();
    if (count($result))
    {
        drupal_json_output($result);
    }
    else
    {
        drupal_not_found();
    }
}

function polls($id) {
    if ($id == "")
    {
        api_call("SELECT n.title,n.vid AS poll_id,DATE_FORMAT(DATE(FROM_UNIXTIME(n.created)),'%d/%m/%Y') AS date,f.body_value AS description 
                  FROM {node} AS n
                  JOIN {field_data_body} AS f ON f.entity_id = n.vid
                  WHERE type='pw_poll' 
                  ORDER BY created DESC");
    }
    else //a specific poll
    {
        api_call("SELECT v.value,v.uid
            FROM {votingapi_vote} AS v 
            WHERE v.entity_id=:id", array(":id" => $id));
    }

}

function constituencies() {
    api_call("SELECT name AS value FROM {taxonomy_term_data} WHERE vid=6 ORDER BY value");
}

function politicians() {

    api_call("SELECT r.uid, CONCAT(f.field_user_fname_value, ' ',l.field_user_lname_value) AS name, 
        g.field_user_gender_value AS gender, t1.name AS constituency, t2.name as party, 0 AS 'vote'
        FROM {users_roles} AS r
        JOIN {field_data_field_user_fname} AS f ON f.entity_id=r.uid
        JOIN {field_data_field_user_lname} AS l ON f.entity_id=l.entity_id 
        JOIN {field_data_field_user_gender} AS g ON g.entity_id=r.uid
        JOIN {field_data_field_user_constituency} AS c ON c.entity_id=r.uid
        JOIN {taxonomy_term_data} AS t1 ON c.field_user_constituency_tid=t1.tid
        JOIN {field_data_field_user_party} AS p ON p.entity_id=r.uid
        JOIN {taxonomy_term_data} AS t2 ON p.field_user_party_tid=t2.tid
        WHERE r.rid=181527986 
        AND f.language='und' 
        AND l.language='und'
        ");
}

function top_trumps() {
    //Get data for random set of politicians for top trumps game.

    $BASE_IMG_URL = 'http://dailwatch.ie/sites/default/files/styles/pw_portrait_l/public/users/';

    api_call("SELECT r.uid, CONCAT(f.field_user_fname_value, ' ',l.field_user_lname_value) AS name, 
        t1.name AS constituency, t2.name as party,
        CONCAT('" . $BASE_IMG_URL . "',fm.filename) AS image,
        attr.number_terms AS terms,
        attr.attendance_2013 AS attendance,
        qs.field_user_questions_get_value AS questions,
        LEAST(100, 100*ans.field_user_answers_give_value/qs.field_user_questions_get_value) AS percent_answered,
        100*votes.votes_present/votes.votes_total AS vote_present
        FROM {users_roles} AS r
        JOIN {field_data_field_user_fname} AS f ON f.entity_id=r.uid
        JOIN {top_trumps_attributes} AS attr ON attr.uid=r.uid
        JOIN {field_data_field_user_lname} AS l ON f.entity_id=l.entity_id 
        JOIN {field_data_field_user_constituency} AS c ON c.entity_id=r.uid
        JOIN {taxonomy_term_data} AS t1 ON c.field_user_constituency_tid=t1.tid
        JOIN {field_data_field_user_party} AS p ON p.entity_id=r.uid
        JOIN {taxonomy_term_data} AS t2 ON p.field_user_party_tid=t2.tid
        JOIN {file_usage} AS fu ON fu.id = r.uid
        JOIN {file_managed} AS fm ON fm.fid = fu.fid
        JOIN (SELECT a.uid AS uid, a.votes_total, p.votes_present 
             FROM 
             (SELECT uid,COUNT(value) AS votes_total 
                FROM {votingapi_vote} AS v GROUP BY UID) AS a
             JOIN 
             (SELECT uid, COUNT(value) AS votes_present 
                FROM {votingapi_vote} WHERE value<>2 GROUP BY uid) AS p
                ON a.uid=p.uid) 
            AS votes ON votes.uid=r.uid
        JOIN field_data_field_user_answers_give AS ans ON r.uid = ans.entity_id
        JOIN field_data_field_user_questions_get AS qs ON r.uid = qs.entity_id
        WHERE r.rid=181527986 
        AND f.language='und' 
        AND l.language='und'
        AND fu.module='file'
        AND r.uid NOT IN (996, 1023)
        ORDER BY RAND()
        LIMIT 16
        ");
}
