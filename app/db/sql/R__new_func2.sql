CREATE OR REPLACE FUNCTION new_func2()
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
        WHERE p.username = '새로운 Function 생성2'
        LIMIT 1;


        RETURN postData;
    END;
$$;