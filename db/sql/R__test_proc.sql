-- DROP PROCEDURE IF EXISTS test_proc;

CREATE OR REPLACE FUNCTION test_proc()
    RETURNS json
    LANGUAGE plpgsql
AS
$$
    DECLARE
        postData JSON;
    BEGIN
        SELECT to_json(p)
        INTO postData
        FROM posts p
        WHERE p.username = '해당 부분을 변경합니다.'
        LIMIT 1;

        RETURN postData;
    END;
$$;